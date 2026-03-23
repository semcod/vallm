"""Import validation: checks that all imported modules are resolvable.

This module provides backward compatibility while using the refactored
language-specific validators in the imports/ subdirectory.
"""

# Import the new refactored system - avoid circular import
from .imports.wrapper import ImportValidator

# Re-export for backward compatibility
__all__ = ["ImportValidator"]
