"""Complexity validation using radon and lizard."""

from __future__ import annotations

from typing import Optional

import lizard
from radon.complexity import cc_visit
from radon.metrics import mi_visit

from vallm.config import VallmSettings
from vallm.core.languages import Language, detect_language, LIZARD_SUPPORTED
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator


class ComplexityValidator(BaseValidator):
    """Tier 2: Cyclomatic complexity, maintainability index, and function metrics."""

    tier = 2
    name = "complexity"
    weight = 1.0

    def __init__(self, settings: Optional[VallmSettings] = None):
        if settings is None:
            settings = VallmSettings()
        self.max_cc = settings.max_cyclomatic_complexity
        self.max_func_length = settings.max_function_length

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        issues: list[Issue] = []
        details: dict = {}

        if proposal.language == "python":
            cc_score, cc_issues, cc_details = self._check_python_complexity(proposal.code)
            issues.extend(cc_issues)
            details.update(cc_details)
        else:
            cc_score = 1.0

        # lizard works for multiple languages
        lz_score, lz_issues, lz_details = self._check_lizard(
            proposal.code, proposal.language, proposal.filename
        )
        issues.extend(lz_issues)
        details.update(lz_details)

        score = min(cc_score, lz_score)

        return ValidationResult(
            validator=self.name,
            score=score,
            weight=self.weight,
            confidence=1.0,
            issues=issues,
            details=details,
        )

    def _check_python_complexity(self, code: str) -> tuple[float, list[Issue], dict]:
        """Check Python-specific complexity with radon."""
        issues = []
        details = {}

        try:
            blocks = cc_visit(code)
            max_cc = 0
            for block in blocks:
                max_cc = max(max_cc, block.complexity)
                if block.complexity > self.max_cc:
                    issues.append(
                        Issue(
                            message=(
                                f"{block.name} has cyclomatic complexity "
                                f"{block.complexity} (max: {self.max_cc})"
                            ),
                            severity=Severity.WARNING,
                            line=block.lineno,
                            rule="complexity.cyclomatic",
                        )
                    )
            details["max_cyclomatic_complexity"] = max_cc
            details["functions_analyzed"] = len(blocks)
        except Exception:
            return 1.0, issues, details

        try:
            mi = mi_visit(code, multi=False)
            details["maintainability_index"] = round(mi, 2)
            if mi < 20:
                issues.append(
                    Issue(
                        message=f"Low maintainability index: {mi:.1f} (threshold: 20)",
                        severity=Severity.WARNING,
                        rule="complexity.maintainability",
                    )
                )
        except Exception:
            pass

        if not issues:
            return 1.0, issues, details

        # Score based on severity
        error_count = sum(1 for i in issues if i.severity == Severity.ERROR)
        warning_count = sum(1 for i in issues if i.severity == Severity.WARNING)
        score = max(0.0, 1.0 - error_count * 0.3 - warning_count * 0.1)
        return score, issues, details

    def _check_lizard(
        self, code: str, language: str, filename: str | None
    ) -> tuple[float, list[Issue], dict]:
        """Check complexity with lizard (multi-language)."""
        issues = []
        details = {}

        # Use Language enum for extension mapping
        lang_obj = detect_language(language) if language else None
        if lang_obj and lang_obj in LIZARD_SUPPORTED:
            ext = lang_obj.extension.lstrip(".")
        elif lang_obj:
            # Fall back to tree-sitter id for unknown lizard languages
            ext_map = {
                "python": "py", "javascript": "js", "typescript": "ts",
                "c": "c", "cpp": "cpp", "java": "java", "go": "go",
                "rust": "rs", "ruby": "rb", "swift": "swift",
                "php": "php", "kotlin": "kt", "scala": "scala",
            }
            ext = ext_map.get(language, language)
        else:
            ext = language
        
        fname = filename or f"proposal.{ext}"

        try:
            result = lizard.analyze_file.analyze_source_code(fname, code)
            details["lizard_functions"] = []
            details["language"] = language
            details["lizard_supported"] = lang_obj in LIZARD_SUPPORTED if lang_obj else False

            for func in result.function_list:
                func_info = {
                    "name": func.name,
                    "complexity": func.cyclomatic_complexity,
                    "length": func.nloc,
                    "tokens": func.token_count,
                    "parameters": func.parameter_count,
                }
                details["lizard_functions"].append(func_info)

                if func.cyclomatic_complexity > self.max_cc:
                    issues.append(
                        Issue(
                            message=(
                                f"{func.name}: CC={func.cyclomatic_complexity} "
                                f"exceeds limit {self.max_cc}"
                            ),
                            severity=Severity.WARNING,
                            line=func.start_line,
                            rule="complexity.lizard_cc",
                        )
                    )
                if func.nloc > self.max_func_length:
                    issues.append(
                        Issue(
                            message=(
                                f"{func.name}: {func.nloc} lines "
                                f"exceeds limit {self.max_func_length}"
                            ),
                            severity=Severity.WARNING,
                            line=func.start_line,
                            rule="complexity.lizard_length",
                        )
                    )
        except Exception:
            pass

        if not issues:
            return 1.0, issues, details

        warning_count = len(issues)
        score = max(0.0, 1.0 - warning_count * 0.15)
        return score, issues, details
