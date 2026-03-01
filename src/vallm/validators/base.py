"""Base validator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from vallm.core.proposal import Proposal
from vallm.scoring import ValidationResult


class BaseValidator(ABC):
    """Base class for all vallm validators."""

    tier: int = 1
    name: str = "base"
    weight: float = 1.0

    @abstractmethod
    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate a proposal and return a result."""
        ...
