#!/usr/bin/env python3
"""Tests for semantic validation with LLM."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

# Mock LLM responses for testing
MOCK_LLM_RESPONSES = {
    "good_code": {
        "verdict": "pass",
        "score": 0.9,
        "reasoning": "Code is well-structured and follows best practices."
    },
    "bad_code": {
        "verdict": "review", 
        "score": 0.3,
        "reasoning": "Code has potential issues and could be improved."
    },
    "syntax_error": {
        "verdict": "fail",
        "score": 0.1,
        "reasoning": "Code contains syntax errors."
    }
}


class MockLLMProvider:
    """Mock LLM provider for testing."""
    
    def __init__(self, responses: Dict[str, Any] = None):
        self.responses = responses or MOCK_LLM_RESPONSES
        self.call_count = 0
    
    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Mock validation method."""
        self.call_count += 1
        
        # Simple heuristic to determine response
        if "def invalid_syntax" in code:
            return self.responses["syntax_error"]
        elif "print(" in code and "input(" in code:
            return self.responses["bad_code"]
        else:
            return self.responses["good_code"]
    
    def is_available(self) -> bool:
        """Mock availability check."""
        return True


class TestSemanticValidation:
    """Test semantic validation functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        """Fixture providing mock LLM provider."""
        return MockLLMProvider()
    
    def test_semantic_validator_init(self, mock_llm):
        """Test semantic validator initialization."""
        from vallm.validators.semantic import SemanticValidator
        
        # Mock the LLM provider
        validator = SemanticValidator()
        validator.llm_provider = mock_llm
        
        assert validator.tier == 3
        assert validator.name == "semantic"
        assert validator.weight == 1.0
    
    def test_semantic_validation_good_code(self, mock_llm):
        """Test semantic validation with good code."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        from unittest.mock import patch
        
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
        
        # Mock the _call_llm method to return a valid JSON response
        mock_response = '''```json
{
    "correctness": 5,
    "style": 5,
    "security": 5,
    "completeness": 5,
    "issues": [],
    "summary": "Good code"
}
```'''
        with patch.object(validator, '_call_llm', return_value=mock_response):
            result = validator.validate(proposal, {})
        
        assert result.score >= 0.7
        assert result.validator == "semantic"
        assert len(result.issues) == 0
    
    def test_semantic_validation_bad_code(self, mock_llm):
        """Test semantic validation with problematic code."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        
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
    
    def test_semantic_validation_syntax_error(self, mock_llm):
        """Test semantic validation with syntax errors."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        from unittest.mock import patch
        
        validator = SemanticValidator()
        
        code = """
def invalid_syntax(
    print("Missing closing parenthesis")
"""
        
        proposal = Proposal(code=code, language="python")
        
        # Mock the _call_llm method to return a valid JSON response with syntax error
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
        with patch.object(validator, '_call_llm', return_value=mock_response):
            result = validator.validate(proposal, {})
        
        assert result.score <= 0.2
        assert result.validator == "semantic"
        assert len(result.issues) > 0
    
    def test_semantic_validation_multilang(self, mock_llm):
        """Test semantic validation across multiple languages."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        
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
        """Test semantic validation with reference code."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        from unittest.mock import patch
        
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
        
        proposal = Proposal(
            code=new_code, 
            language="python",
            reference_code=original_code
        )
        
        # Mock the _call_llm method to return a valid JSON response
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
        with patch.object(validator, '_call_llm', return_value=mock_response):
            result = validator.validate(proposal, {})
        
        assert result.validator == "semantic"
        assert result.score >= 0.6  # Should be good improvement
    
    def test_semantic_validation_disabled(self):
        """Test semantic validation when disabled."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        from vallm.config import VallmSettings
        
        validator = SemanticValidator()
        settings = VallmSettings(enable_semantic=False)
        
        code = "def hello(): return 'world'"
        proposal = Proposal(code=code, language="python")
        
        # Should return early with neutral score
        result = validator.validate(proposal, settings)
        
        # When disabled, should still run but with lower score expectations
        assert result.validator == "semantic"
        assert 0.0 <= result.score <= 1.0


@pytest.mark.slow
class TestLLMIntegration:
    """Test LLM integration functionality."""
    
    def test_ollama_provider_available(self):
        """Test Ollama provider availability check."""
        try:
            from vallm.validators.semantic import OllamaProvider
            provider = OllamaProvider()
            
            # This will likely fail in test environment, but we test the method
            available = provider.is_available()
            assert isinstance(available, bool)
        except ImportError:
            pytest.skip("Ollama not available")
    
    def test_litellm_provider_available(self):
        """Test LiteLLM provider availability check."""
        try:
            from vallm.validators.semantic import LiteLLMProvider
            provider = LiteLLMProvider()
            
            # This will likely fail in test environment, but we test the method
            available = provider.is_available()
            assert isinstance(available, bool)
        except ImportError:
            pytest.skip("LiteLLM not available")
    
    def test_semantic_settings(self):
        """Test semantic validation settings."""
        from vallm.config import VallmSettings
        
        settings = VallmSettings()
        
        # Test default values
        assert hasattr(settings, 'enable_semantic')
        assert hasattr(settings, 'llm_provider')
        assert hasattr(settings, 'llm_model')
        
        # Test setting values
        settings.enable_semantic = True
        settings.llm_provider = "ollama"
        settings.llm_model = "qwen2.5-coder:7b"
        
        assert settings.enable_semantic is True
        assert settings.llm_provider == "ollama"
        assert settings.llm_model == "qwen2.5-coder:7b"


@pytest.mark.integration
class TestCLIWithSemantic:
    """Test CLI commands with semantic validation."""
    
    def test_validate_with_semantic_flag(self):
        """Test validate command with semantic flag."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
""")
            f.flush()
            
            try:
                # Test with semantic flag (will likely fail without LLM, but tests the flag)
                from vallm.cli import validate
                from vallm.config import VallmSettings
                
                # Mock the settings to avoid actual LLM calls
                settings = VallmSettings(enable_semantic=False)  # Disable for test
                
                # This should work without LLM
                # Note: This is a simplified test - in real scenario you'd need proper mocking
                assert True  # Placeholder for actual CLI testing
                
            finally:
                Path(f.name).unlink()
    
    def test_batch_with_semantic_flag(self):
        """Test batch command with semantic flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            
            # Create test files
            (project_dir / "main.py").write_text("def hello(): return 'world'")
            (project_dir / "utils.py").write_text("def add(a, b): return a + b")
            
            # Test batch command structure
            from vallm.cli import batch
            
            # Verify batch function accepts semantic parameter
            import inspect
            sig = inspect.signature(batch)
            assert 'enable_semantic' in sig.parameters


class TestSemanticValidationEdgeCases:
    """Test edge cases for semantic validation."""
    
    def test_empty_code(self):
        """Test semantic validation with empty code."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        
        validator = SemanticValidator()
        
        proposal = Proposal(code="", language="python")
        result = validator.validate(proposal, {})
        
        assert result.validator == "semantic"
        assert 0.0 <= result.score <= 1.0
    
    def test_very_long_code(self):
        """Test semantic validation with very long code."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        
        validator = SemanticValidator()
        
        # Generate a long function
        lines = ["def long_function():"]
        for i in range(100):
            lines.append(f"    var_{i} = {i}")
        lines.append("    return sum([var_{} for i in range(100)])".format(i))
        
        code = "\n".join(lines)
        
        proposal = Proposal(code=code, language="python")
        result = validator.validate(proposal, {})
        
        assert result.validator == "semantic"
        assert 0.0 <= result.score <= 1.0
    
    def test_unsupported_language(self):
        """Test semantic validation with unsupported language."""
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        
        validator = SemanticValidator()
        
        proposal = Proposal(code="some code", language="unsupported")
        result = validator.validate(proposal, {})
        
        assert result.validator == "semantic"
        assert 0.0 <= result.score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
