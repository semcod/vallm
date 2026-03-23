"""Backward compatibility wrapper for ImportValidator."""

from typing import Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import ValidationResult
from vallm.validators.base import BaseValidator
from .factory import ImportValidatorFactory


class ImportValidator(BaseValidator):
    """Backward compatibility wrapper for the refactored import validation system."""
    
    tier = 1
    name = "imports"
    weight = 1.5

    def validate(self, proposal: Proposal, context: Dict[str, Any]) -> ValidationResult:
        """Validate imports by dispatching to language-specific validators."""
        try:
            validator = ImportValidatorFactory.create_validator(proposal.language)
            return validator.validate(proposal, context)
        except ValueError:
            # Unsupported language - return skipped result
            return ValidationResult(
                validator="imports",
                score=1.0,  # Neutral score
                weight=self.weight,
                issues=[],
                details={"skipped": f"unsupported language: {proposal.language}"},
            )
