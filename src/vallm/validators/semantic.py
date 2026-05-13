"""Semantic validation using LLM-as-judge (Ollama, litellm, or direct HTTP)."""

from __future__ import annotations

import json
import re
from typing import Optional

from vallm.config import VallmSettings
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator

_REVIEW_PROMPT = """\
You are an expert code reviewer. Analyze the following code proposal and provide a structured review.

## Code to Review
```{language}
{code}
```

{reference_section}

## Instructions
Evaluate the code on these criteria (score each 1-5):
1. **Correctness**: Does the code work as intended? Are there logical errors?
2. **Style**: Does it follow language conventions and best practices?
3. **Security**: Are there security vulnerabilities?
4. **Completeness**: Does it handle edge cases?

Respond ONLY with valid JSON in this exact format:
{{
    "correctness": <1-5>,
    "style": <1-5>,
    "security": <1-5>,
    "completeness": <1-5>,
    "issues": [
        {{"message": "<issue description>", "severity": "error|warning|info", "line": <line_number_or_null>}}
    ],
    "summary": "<one sentence summary>"
}}
"""


class SemanticValidator(BaseValidator):
    """Tier 3: LLM-as-judge semantic code review."""

    tier = 3
    name = "semantic"
    weight = 1.0

    def __init__(self, settings: Optional[VallmSettings] = None):
        if settings is None:
            settings = VallmSettings()
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.base_url = settings.llm_base_url
        self.temperature = settings.llm_temperature

        # Initialize cache for performance
        from vallm.validators.semantic_cache import get_semantic_cache

        self.cache = get_semantic_cache()

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        # Check cache first
        cached_result = self.cache.get(proposal.code, proposal.language, self.model)
        if cached_result is not None:
            return cached_result

        prompt = self._build_prompt(proposal)

        try:
            response_text = self._call_llm(prompt)
            result = self._parse_response(response_text)

            # Cache the result
            self.cache.set(proposal.code, proposal.language, self.model, result)

            return result
        except Exception as e:
            return ValidationResult(
                validator=self.name,
                score=0.0,
                weight=self.weight,
                confidence=0.1,
                issues=[
                    Issue(
                        message=f"LLM review failed: {e}",
                        severity=Severity.INFO,
                        rule="semantic.llm_error",
                    )
                ],
                details={"error": str(e)},
            )

    def _build_prompt(self, proposal: Proposal) -> str:
        reference_section = ""
        if proposal.reference_code:
            reference_section = (
                f"## Reference Code (existing implementation)\n"
                f"```{proposal.language}\n{proposal.reference_code}\n```\n"
                f"Compare the proposal against this reference."
            )

        return _REVIEW_PROMPT.format(
            language=proposal.language,
            code=proposal.code,
            reference_section=reference_section,
        )

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM backend. Tries ollama first, then litellm, then HTTP."""
        if self.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.provider == "litellm":
            return self._call_litellm(prompt)
        else:
            return self._call_http(prompt)

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama using the ollama Python package."""
        try:
            import ollama

            client = ollama.Client(host=self.base_url)
            response = client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": self.temperature},
            )
            return response["message"]["content"]
        except ImportError:
            # Fallback to HTTP if ollama package not installed
            return self._call_http(prompt)

    def _call_litellm(self, prompt: str) -> str:
        """Call via litellm for multi-provider support."""
        try:
            import litellm
        except ImportError:
            raise ImportError("litellm package is required. Install with: pip install litellm")

        response = litellm.completion(
            model=f"ollama/{self.model}" if self.provider == "ollama" else self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            api_base=self.base_url,
        )
        return response.choices[0].message.content

    def _call_http(self, prompt: str) -> str:
        """Direct HTTP call to Ollama API (no external deps needed)."""
        import urllib.request

        url = f"{self.base_url}/api/chat"
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": self.temperature},
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["message"]["content"]

    def _parse_response(self, response_text: str) -> ValidationResult:
        """Parse LLM JSON response into a ValidationResult."""
        if not isinstance(response_text, str):
            return self._create_parse_error_result(str(response_text))

        json_str = self._extract_json_from_response(response_text)
        if json_str is None:
            return self._create_parse_error_result(response_text)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return self._create_json_error_result(response_text)

        scores = self._parse_scores(data)
        issues = self._parse_issues(data)
        avg_score = sum(scores.values()) / len(scores) if scores else 0.0

        return ValidationResult(
            validator=self.name,
            score=avg_score,
            weight=self.weight,
            confidence=0.7,
            issues=issues,
            details={
                "scores": scores,
                "summary": data.get("summary", ""),
                "model": self.model,
            },
        )

    def _extract_json_from_response(self, response_text: str) -> Optional[str]:
        """Extract JSON from response (handle markdown code blocks)."""
        # Try to find JSON in markdown code blocks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if json_match:
            return json_match.group(1)

        # Try to find raw JSON
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", response_text, re.DOTALL)
        if json_match:
            return json_match.group(0)

        return None

    def _create_parse_error_result(self, response_text: str) -> ValidationResult:
        """Create result for when JSON cannot be parsed from response."""
        return ValidationResult(
            validator=self.name,
            score=0.0,
            weight=self.weight,
            confidence=0.3,
            issues=[
                Issue(
                    message="Could not parse LLM response as JSON",
                    severity=Severity.INFO,
                    rule="semantic.parse_error",
                )
            ],
            details={"raw_response": response_text[:500]},
        )

    def _create_json_error_result(self, response_text: str) -> ValidationResult:
        """Create result for when JSON is invalid."""
        return ValidationResult(
            validator=self.name,
            score=0.0,
            weight=self.weight,
            confidence=0.3,
            issues=[
                Issue(
                    message="Invalid JSON in LLM response",
                    severity=Severity.INFO,
                    rule="semantic.json_error",
                )
            ],
            details={"raw_response": response_text[:500]},
        )

    def _parse_scores(self, data: dict) -> dict:
        """Parse and normalize scores from LLM response."""
        scores = {}
        for key in ("correctness", "style", "security", "completeness"):
            val = data.get(key, 3)
            if isinstance(val, (int, float)):
                scores[key] = max(0.0, min(1.0, (val - 1) / 4))
            else:
                scores[key] = 0.5
        return scores

    def _parse_issues(self, data: dict) -> list:
        """Parse issues from LLM response."""
        issues = []
        for item in data.get("issues", []):
            if not isinstance(item, dict):
                continue

            severity = self._parse_severity(item.get("severity", "info"))
            line = self._parse_line_number(item.get("line"))

            issues.append(
                Issue(
                    message=item.get("message", "Unknown issue"),
                    severity=severity,
                    line=line,
                    rule="semantic.llm_judge",
                )
            )
        return issues

    def _parse_severity(self, severity_str: str) -> Severity:
        """Parse severity string into Severity enum."""
        severity_map = {
            "error": Severity.ERROR,
            "warning": Severity.WARNING,
            "info": Severity.INFO,
        }
        return severity_map.get(severity_str.lower(), Severity.INFO)

    def _parse_line_number(self, line) -> Optional[int]:
        """Parse line number from various formats."""
        if isinstance(line, int):
            return line

        if isinstance(line, str):
            try:
                return int(line)
            except (ValueError, TypeError):
                return None

        return None
