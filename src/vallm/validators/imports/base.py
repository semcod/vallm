"""Base class for language-specific import validators."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult


class BaseImportValidator(ABC):
    """Base class for all import validators."""
    
    tier = 1
    weight = 1.5
    
    @abstractmethod
    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate imports for a specific language."""
        pass
    
    @abstractmethod
    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from code."""
        pass
    
    @abstractmethod
    def module_exists(self, module_name: str) -> bool:
        """Check if a module/package exists."""
        pass
    
    def create_validation_result(self, issues: List[Issue], checked: int, 
                               found: int, language: str) -> ValidationResult:
        """Create a standardized validation result."""
        return ValidationResult(
            validator=f"imports.{language}",
            score=1.0 - len(issues) / max(checked, 1),
            weight=self.weight,
            issues=issues,
            details={"checked": checked, "found": found, "language": language},
        )
