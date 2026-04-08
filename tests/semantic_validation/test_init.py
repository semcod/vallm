"""Semantic validator initialization tests."""

import pytest


class TestSemanticValidationInit:
    """Test semantic validator initialization functionality."""

    @pytest.fixture
    def mock_llm(self):
        from .fixtures import MockLLMProvider

        return MockLLMProvider()

    def test_semantic_validator_init(self, mock_llm):
        from vallm.validators.semantic import SemanticValidator

        validator = SemanticValidator()
        validator.llm_provider = mock_llm

        assert validator.tier == 3
        assert validator.name == "semantic"
        assert validator.weight == 1.0
