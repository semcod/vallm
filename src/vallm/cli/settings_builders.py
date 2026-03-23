"""Settings builders for vallm CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from vallm.config import VallmSettings


def build_validate_settings(
    config: Optional[Path],
    enable_semantic: bool,
    enable_security: bool,
    model: Optional[str],
    verbose: bool,
) -> VallmSettings:
    """Build settings for validation command."""
    # Load base settings
    if config:
        settings = VallmSettings.from_toml(config)
    else:
        settings = VallmSettings()
    
    # Override with command line options
    if enable_semantic:
        settings.enable_semantic = enable_semantic
    if enable_security:
        settings.enable_security = enable_security
    if model:
        settings.llm_model = model
    if verbose:
        settings.verbose = verbose
    
    return settings


def build_batch_settings(
    enable_semantic: bool,
    enable_security: bool,
    model: Optional[str],
    verbose: bool,
    no_imports: bool,
    no_complexity: bool,
) -> VallmSettings:
    """Load and configure settings for batch validation."""
    settings = VallmSettings()
    
    # Override with command line options
    settings.enable_semantic = enable_semantic
    settings.enable_security = enable_security
    if model:
        settings.llm_model = model
    settings.verbose = verbose
    settings.enable_imports = not no_imports
    settings.enable_complexity = not no_complexity
    
    return settings
