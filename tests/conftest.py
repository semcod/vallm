#!/usr/bin/env python3
"""Shared pytest configuration and fixtures."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file with simple code."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
def hello_world():
    return "Hello, World!"

def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    print(hello_world())
    print(add(2, 3))
""")
        f.flush()
        yield Path(f.name)
        f.close()
    Path(f.name).unlink()


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider to avoid external API calls."""
    mock_provider = Mock()
    mock_provider.is_available.return_value = False
    mock_provider.validate_code.return_value = {
        "verdict": "pass",
        "score": 0.8,
        "reasoning": "Mock validation"
    }
    return mock_provider


@pytest.fixture(autouse=True)
def disable_external_calls():
    """Automatically disable external API calls in tests."""
    with patch('requests.post'), \
         patch('ollama.Client'), \
         patch('litellm.completion'):
        yield


# Add markers to pytest
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
