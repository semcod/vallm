"""vallm - A complete toolkit for validating LLM-generated code."""

from vallm.config import VallmSettings
from vallm.core.proposal import Proposal
from vallm.scoring import ValidationResult, Verdict, Issue, validate

__all__ = [
    "validate",
    "Proposal",
    "ValidationResult",
    "Verdict",
    "Issue",
    "VallmSettings",
]

__version__ = "0.1.4"
