"""Factory for creating language-specific import validators."""

from typing import List, Dict, Type
from .base import BaseImportValidator
from .python_imports import PythonImportValidator
from .javascript_imports import JavaScriptImportValidator
from .go_imports import GoImportValidator
from .rust_imports import RustImportValidator
from .java_imports import JavaImportValidator
from .c_imports import CImportValidator


class ImportValidatorFactory:
    """Factory for creating language-specific import validators."""

    _validators: Dict[str, Type[BaseImportValidator]] = {
        "python": PythonImportValidator,
        "javascript": JavaScriptImportValidator,
        "typescript": JavaScriptImportValidator,  # Reuse JS validator
        "go": GoImportValidator,
        "rust": RustImportValidator,
        "java": JavaImportValidator,
        "c": CImportValidator,
        "cpp": CImportValidator,
    }

    @classmethod
    def create_validator(cls, language: str) -> BaseImportValidator:
        """Create a validator for the specified language."""
        validator_class = cls._validators.get(language)
        if not validator_class:
            raise ValueError(f"Unsupported language: {language}")
        return validator_class()

    @classmethod
    def supported_languages(cls) -> List[str]:
        """Get list of supported languages."""
        return list(cls._validators.keys())

    @classmethod
    def register_validator(cls, language: str, validator_class: Type[BaseImportValidator]):
        """Register a new validator for a language."""
        cls._validators[language] = validator_class
