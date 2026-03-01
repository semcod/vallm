"""pluggy hook specifications for vallm validators."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pluggy

if TYPE_CHECKING:
    from vallm.core.proposal import Proposal
    from vallm.scoring import ValidationResult

hookspec = pluggy.HookspecMarker("vallm")
hookimpl = pluggy.HookimplMarker("vallm")


class VallmSpec:
    """Hook specifications that validators must implement."""

    @hookspec
    def validate_proposal(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate a code proposal and return a ValidationResult."""
        ...

    @hookspec
    def get_validator_name(self) -> str:
        """Return the name of this validator."""
        ...

    @hookspec
    def get_validator_tier(self) -> int:
        """Return the tier (1-4) of this validator for pipeline ordering."""
        ...
