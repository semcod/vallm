"""Base class for language-specific import validators."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult


class BaseImportValidator(ABC):
    """Base class for all import validators."""

    tier = 1
    weight = 1.5

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate imports using common pattern."""
        issues = []
        imports = self.extract_imports(proposal.code)

        for import_info in imports:
            module_name = import_info["module"]
            line = import_info["line"]

            if not self.module_exists(module_name):
                issues.append(
                    Issue(
                        message=self._get_error_message(module_name),
                        severity=Severity.WARNING,
                        line=line,
                        rule=self._get_rule_name(),
                    )
                )

        return self.create_validation_result(
            issues, len(imports), len(imports) - len(issues), self.get_language()
        )

    @abstractmethod
    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from code."""
        pass

    @abstractmethod
    def module_exists(self, module_name: str) -> bool:
        """Check if a module/package exists."""
        pass

    @abstractmethod
    def get_language(self) -> str:
        """Get the language identifier."""
        pass

    @abstractmethod
    def _get_error_message(self, module_name: str) -> str:
        """Get error message for missing module."""
        pass

    @abstractmethod
    def _get_rule_name(self) -> str:
        """Get rule name for validation errors."""
        pass

    def create_validation_result(
        self, issues: List[Issue], checked: int, found: int, language: str
    ) -> ValidationResult:
        """Create a standardized validation result."""
        return ValidationResult(
            validator=f"imports.{language}",
            score=1.0 - len(issues) / max(checked, 1),
            weight=self.weight,
            issues=issues,
            details={"checked": checked, "found": found, "language": language},
        )
