import pytest
from tests.mock_llm_provider import MockLLMProvider


class TestSemanticValidation:
    @pytest.fixture(scope="class")
    def mock_llm(self):
        return MockLLMProvider()

    def test_semantic_validator_init(self, mock_llm):
        from vallm.validators.semantic import SemanticValidator

        validator = SemanticValidator()
        validator.llm_provider = mock_llm
        assert validator.tier == 3
        assert validator.name == "semantic"
        assert validator.weight == 1.0

    def test_semantic_validation_good_code(self, mock_llm):
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
    result = eval(data)  # Dangerous eval
    return result
"""
        proposal = Proposal(code=code, language="python")
        result = validator.validate(proposal, {})
        assert result.score <= 0.5
        assert result.validator == "semantic"
        assert len(result.issues) > 0

    def test_semantic_validation_syntax_error(self, mock_llm):
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        from unittest.mock import patch

        validator = SemanticValidator()
        validator.cache.clear()
        code = """
def invalid_syntax(
    print("Missing closing parenthesis")
"""
        proposal = Proposal(code=code, language="python")
        mock_response = """```json
{
    "correctness": 1,
    "style": 1,
    "security": 1,
    "completeness": 1,
    "issues": [{"message": "Syntax error", "severity": "error", "line": 2}],
    "summary": "Has syntax errors"
}
```"""
        with patch.object(validator, "_call_llm", return_value=mock_response):
            result = validator.validate(proposal, {})
        assert result.score <= 0.3
        assert result.validator == "semantic"
        assert len(result.issues) > 0

    def test_semantic_validation_multilang(self, mock_llm):
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal

        validator = SemanticValidator()
        validator.llm_provider = mock_llm
        test_cases = [
            ("python", "def hello(): return 'world'"),
            ("javascript", "function hello() { return 'world'; }"),
            ("go", "package main\nfunc main() { println('Hello, World!') }"),
            ("rust", 'fn main() { println!("Hello, World!"); }'),
        ]
        for language, code in test_cases:
            proposal = Proposal(code=code, language=language)
            result = validator.validate(proposal, {})
            assert result.validator == "semantic"
            assert 0.0 <= result.score <= 1.0

    def test_semantic_validation_with_reference(self, mock_llm):
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
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return a + b
"""
        proposal = Proposal(code=new_code, language="python", reference_code=original_code)
        mock_response = """```json
{
    "correctness": 5,
    "style": 4,
    "security": 5,
    "completeness": 5,
    "issues": [],
    "summary": "Improved code with validation"
}
```"""
        with patch.object(validator, "_call_llm", return_value=mock_response):
            result = validator.validate(proposal, {})
        assert result.validator == "semantic"
        assert result.score >= 0.6

    def test_semantic_validation_disabled(self):
        from vallm.validators.semantic import SemanticValidator
        from vallm.core.proposal import Proposal
        from vallm.config import VallmSettings

        validator = SemanticValidator()
        settings = VallmSettings(enable_semantic=False)
        code = "def hello(): return 'world'"
        proposal = Proposal(code=code, language="python")
        result = validator.validate(proposal, {})
