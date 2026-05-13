"""Semantic validator tests for good and problematic code."""

from unittest.mock import patch

import pytest

from .fixtures import MockLLMProvider


class TestSemanticValidationCodeQuality:
    """Test semantic validation for code quality scenarios."""

    @pytest.fixture(scope="class")
    def mock_llm(self):
        return MockLLMProvider()

    def test_semantic_validation_good_code(self, mock_llm):
        from vallm.core.proposal import Proposal
        from vallm.validators.semantic import SemanticValidator

        validator = SemanticValidator()
        code = """
def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
"""
        proposal = Proposal(code=code, language="python")
        mock_response = """```json
{
    "correctness": 5,
    "style": 5,
    "security": 5,
    "completeness": 5,
    "issues": [],
    "summary": "Good code"
}
```"""
        with patch.object(validator, "_call_llm", return_value=mock_response):
            result = validator.validate(proposal, {})

        assert result.score >= 0.7
        assert result.validator == "semantic"
        assert len(result.issues) == 0

    def test_semantic_validation_bad_code(self, mock_llm):
        from vallm.core.proposal import Proposal
        from vallm.validators.semantic import SemanticValidator

        validator = SemanticValidator()
        validator.llm_provider = mock_llm
        code = """
def get_user_input():
    name = input("Enter your name: ")
    print("Hello", name)
    return name

def process_data(data):
    # No input validation
    result = eval(data)  # Dangerous eval
    return result
"""
        proposal = Proposal(code=code, language="python")
        result = validator.validate(proposal, {})

        assert result.score <= 0.5
        assert result.validator == "semantic"
        assert len(result.issues) > 0
