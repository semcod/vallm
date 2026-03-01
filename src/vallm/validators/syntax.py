"""Syntax validation via ast.parse and tree-sitter."""

from __future__ import annotations

import ast

from vallm.core.ast_compare import tree_sitter_error_count
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator


class SyntaxValidator(BaseValidator):
    """Tier 1: Fast syntax validation."""

    tier = 1
    name = "syntax"
    weight = 2.0

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        issues: list[Issue] = []
        score = 1.0

        if proposal.language == "python":
            score, issues = self._validate_python(proposal.code)
        else:
            score, issues = self._validate_treesitter(proposal.code, proposal.language)

        return ValidationResult(
            validator=self.name,
            score=score,
            weight=self.weight,
            confidence=1.0,
            issues=issues,
        )

    def _validate_python(self, code: str) -> tuple[float, list[Issue]]:
        """Validate Python syntax using ast.parse and tree-sitter."""
        issues = []

        # ast.parse check
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(
                Issue(
                    message=f"SyntaxError: {e.msg}",
                    severity=Severity.ERROR,
                    line=e.lineno,
                    column=e.offset,
                    rule="syntax.parse",
                )
            )
            return 0.0, issues

        # tree-sitter error check (catches more edge cases)
        try:
            errors = tree_sitter_error_count(code, "python")
            if errors > 0:
                issues.append(
                    Issue(
                        message=f"tree-sitter found {errors} parse error(s)",
                        severity=Severity.WARNING,
                        rule="syntax.tree_sitter",
                    )
                )
                return max(0.0, 1.0 - errors * 0.2), issues
        except Exception:
            pass  # tree-sitter not critical if ast.parse passed

        return 1.0, issues

    def _validate_treesitter(self, code: str, language: str) -> tuple[float, list[Issue]]:
        """Validate non-Python syntax using tree-sitter."""
        issues = []
        try:
            errors = tree_sitter_error_count(code, language)
            if errors > 0:
                issues.append(
                    Issue(
                        message=f"tree-sitter found {errors} parse error(s) in {language}",
                        severity=Severity.ERROR,
                        rule="syntax.tree_sitter",
                    )
                )
                return 0.0, issues
            return 1.0, issues
        except Exception as e:
            issues.append(
                Issue(
                    message=f"Could not parse {language}: {e}",
                    severity=Severity.WARNING,
                    rule="syntax.unsupported",
                )
            )
            return 0.5, issues
