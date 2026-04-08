"""Semantic validator tests for syntax errors, multi-language support, references, and disabled mode."""

from unittest.mock import patch

import pytest

from .fixtures import MockLLMProvider


class TestSemanticValidationAdvanced:
    """Advanced semantic validation scenarios."""

    @pytest.fixture
    def mock_llm(self):
        return MockLLMProvider()

    def test_semantic_validation_syntax_error(self, mock_llm):
        from vallm.core.proposal import Proposal
        from vallm.validators.semantic import SemanticValidator

        validator = SemanticValidator()
        validator.cache.clear()
        code = """
def invalid_syntax(
    print("Missing closing parenthesis")
"""
        proposal = Proposal(code=code, language="python")
        mock_response = '''```json
{
    "correctness": 1,
    "style": 1,
    "security": 1,
    "completeness": 1,
    "issues": [{"message": "Syntax error", "severity": "error", "line": 2}],
    "summary": "Has syntax errors"
}
```'''
        with patch.object(validator, "_call_llm", return_value=mock_response):
            result = validator.validate(proposal, {})

        assert result.score <= 0.3
        assert result.validator == "semantic"
        assert len(result.issues) > 0

    def test_semantic_validation_multilang(self, mock_llm):
        from vallm.core.proposal import Proposal
        from vallm.validators.semantic import SemanticValidator

        validator = SemanticValidator()
        validator.llm_provider = mock_llm
        test_cases = [
            ("python", "def hello(): return 'world'"),
            ("javascript", "function hello() { return 'world'; }"),
            ("go", "package main\nfunc main() { println('Hello, World!') }"),
            ("rust", "fn main() { println!(\"Hello, World!\"); }"),
        ]
        for language, code in test_cases:
            proposal = Proposal(code=code, language=language)
            result = validator.validate(proposal, {})
            assert result.validator == "semantic"
            assert 0.0 <= result.score <= 1.0

    def test_semantic_validation_with_reference(self, mock_llm):
        from vallm.core.proposal import Proposal
        from vallm.validators.semantic import SemanticValidator

        validator = SemanticValidator()
        original_code = """
def calculate_sum(a, b):
    return a + b
"""
        new_code = """
def calculate_sum(a, b):
    # Added input validation
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return a + b
"""
        proposal = Proposal(code=new_code, language="python", reference_code=original_code)
        mock_response = '''```json
{
    "correctness": 5,
    "style": 4,
    "security": 5,
    "completeness": 5,
    "issues": [],
    "summary": "Improved code with validation"
}
```'''
        with patch.object(validator, "_call_llm", return_value=mock_response):
            result = validator.validate(proposal, {})

        assert result.validator == "semantic"
        assert result.score >= 0.6

    def test_semantic_validation_disabled(self):
        from vallm.config import VallmSettings
        from vallm.core.proposal import Proposal
        from vallm.validators.semantic import SemanticValidator

        validator = SemanticValidator()
        settings = VallmSettings(enable_semantic=False)
        code = "def hello(): return 'world'"
        proposal = Proposal(code=code, language="python")
        result = validator.validate(proposal, {})

        assert result.validator == "semantic"
        assert result.score == 0.0
