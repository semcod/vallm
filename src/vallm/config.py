"""Configuration management via pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VallmSettings(BaseSettings):
    """vallm configuration with layered sources: defaults → TOML → env → CLI."""

    model_config = SettingsConfigDict(
        env_prefix="VALLM_",
    )

    # Scoring thresholds
    pass_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    review_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    # Validator toggles
    enable_syntax: bool = True
    enable_imports: bool = True
    enable_complexity: bool = True
    enable_security: bool = False
    enable_semantic: bool = False

    # Complexity limits
    max_cyclomatic_complexity: int = 15
    max_cognitive_complexity: int = 20
    max_function_length: int = 100

    # LLM settings (for semantic validator)
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5-coder:7b"
    llm_base_url: str = "http://localhost:11434"
    llm_temperature: float = 0.1

    # Sandbox settings
    sandbox_backend: str = "subprocess"
    sandbox_timeout: int = 30
    sandbox_memory_limit: str = "256m"

    # Output
    output_format: str = "rich"
    verbose: bool = False

    # Language detection
    default_language: str = "python"

    @classmethod
    def from_toml(cls, path: Optional[Path] = None) -> VallmSettings:
        """Load settings, optionally from a specific TOML file."""
        if path and path.exists():
            return cls(_toml_file=str(path))
        return cls()
