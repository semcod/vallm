"""Proposal model representing code to be validated."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Proposal:
    """A code proposal to be validated.

    Attributes:
        code: The proposed source code string.
        language: Programming language (e.g., 'python', 'javascript', 'c').
        reference_code: Optional reference/existing code for comparison.
        filename: Optional filename for context.
        metadata: Additional metadata (e.g., prompt, model name).
    """

    code: str
    language: str = "python"
    reference_code: Optional[str] = None
    filename: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def code_bytes(self) -> bytes:
        """Return code as bytes for tree-sitter parsing."""
        return self.code.encode("utf-8")

    @property
    def reference_bytes(self) -> Optional[bytes]:
        """Return reference code as bytes for tree-sitter parsing."""
        if self.reference_code is None:
            return None
        return self.reference_code.encode("utf-8")
