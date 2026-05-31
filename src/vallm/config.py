"""Configuration management via pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Global settings instance
_settings: Optional[VallmSettings] = None


class VallmSettings(BaseSettings):
    """vallm configuration with layered sources: defaults → TOML → env → CLI."""

    model_config = SettingsConfigDict(
        env_prefix="VALLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    # Scoring thresholds
    pass_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    review_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    # Validator toggles
    enable_syntax: bool = True
    enable_imports: bool = True
    enable_complexity: bool = True
    enable_security: bool = False
    enable_regression: bool = False
    enable_semantic: bool = False
    enable_intract: bool = False

    # Intract settings
    intract_manifest: str = "intent.yaml"
    intract_mode: str = "project"
    intract_fail_on: str = "violation,missing_required_p1,invalid_manifest"
    intract_warn_on: str = "partial,unknown"
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

    # Output file configurations
    default_toon_filename: str = Field(
        default="validation.toon.yaml", description="Default filename for toon format output"
    )
    default_json_filename: str = Field(
        default="validation.json", description="Default filename for JSON format output"
    )
    default_yaml_filename: str = Field(
        default="validation.yaml", description="Default filename for YAML format output"
    )
    default_txt_filename: str = Field(
        default="validation.txt", description="Default filename for text format output"
    )

    # Cache settings
    semantic_cache_enabled: bool = Field(
        default=True, description="Enable semantic validation cache"
    )
    semantic_cache_ttl: int = Field(default=3600, description="Semantic cache TTL in seconds")

    # Performance settings
    max_concurrent_validations: int = Field(
        default=4, description="Maximum concurrent validation tasks"
    )
    timeout_seconds: int = Field(default=300, description="Timeout for validation operations")

    @classmethod
    def from_toml(cls, path: Optional[Path] = None) -> VallmSettings:
        """Load settings, optionally from a specific TOML file."""
        if path and path.exists():
            return cls(_toml_file=str(path))
        return cls()


def get_settings() -> VallmSettings:
    """Get global settings instance, loading from .env if available."""
    global _settings
    if _settings is None:
        # Check for local .env file first
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            _settings = VallmSettings(_env_file=str(env_file))
        else:
            _settings = VallmSettings()
    return _settings


def reload_settings() -> VallmSettings:
    """Reload settings from environment variables."""
    global _settings
    _settings = None
    return get_settings()


# Convenience functions for common settings
def get_default_filenames() -> dict[str, str]:
    """Get default output filenames by format."""
    settings = get_settings()
    return {
        "toon": settings.default_toon_filename,
        "json": settings.default_json_filename,
        "yaml": settings.default_yaml_filename,
        "txt": settings.default_txt_filename,
    }


def get_default_output_format() -> str:
    """Get default output format."""
    return get_settings().output_format


def get_default_language() -> str:
    """Get default programming language."""
    return get_settings().default_language
