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

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        prompt = self._build_prompt(proposal)

        try:
            response_text = self._call_llm(prompt)
            return self._parse_response(response_text)
        except Exception as e:
            return ValidationResult(
                validator=self.name,
                score=0.5,
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
        import litellm

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
        payload = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": self.temperature},
        }).encode("utf-8")

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
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                return ValidationResult(
                    validator=self.name,
                    score=0.5,
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

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return ValidationResult(
                validator=self.name,
                score=0.5,
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

        # Convert 1-5 scores to 0.0-1.0
        scores = {}
        for key in ("correctness", "style", "security", "completeness"):
            val = data.get(key, 3)
            if isinstance(val, (int, float)):
                scores[key] = max(0.0, min(1.0, (val - 1) / 4))
            else:
                scores[key] = 0.5

        avg_score = sum(scores.values()) / len(scores) if scores else 0.5

        # Parse issues
        issues = []
        for item in data.get("issues", []):
            if isinstance(item, dict):
                sev_str = item.get("severity", "info").lower()
                severity = {
                    "error": Severity.ERROR,
                    "warning": Severity.WARNING,
                    "info": Severity.INFO,
                }.get(sev_str, Severity.INFO)

                line = item.get("line")
                if isinstance(line, str):
                    try:
                        line = int(line)
                    except (ValueError, TypeError):
                        line = None

                issues.append(
                    Issue(
                        message=item.get("message", "Unknown issue"),
                        severity=severity,
                        line=line if isinstance(line, int) else None,
                        rule="semantic.llm_judge",
                    )
                )

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
