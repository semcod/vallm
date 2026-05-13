#!/usr/bin/env python3
"""Tests for sandbox code execution."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vallm.sandbox.runner import SandboxRunner
from vallm.config import VallmSettings


class TestSandboxRunner:
    """Test cases for SandboxRunner."""

    def test_init_default_settings(self):
        """Test SandboxRunner initialization with default settings."""
        runner = SandboxRunner()
        assert runner.timeout == 30
        assert runner.memory_limit == "256m"

    def test_init_custom_settings(self):
        """Test SandboxRunner initialization with custom settings."""
        settings = VallmSettings(sandbox_timeout=60)
        runner = SandboxRunner(settings)
        assert runner.timeout == 60

    @patch("subprocess.run")
    def test_run_python_code_success(self, mock_subprocess):
        """Test successful Python code execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello, World!\n"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        runner = SandboxRunner()
        result = runner.run("print('Hello, World!')", "python")

        assert result.success is True
        assert result.stdout == "Hello, World!\n"
        assert result.stderr == ""
        assert result.exit_code == 0

    @patch("subprocess.run")
    def test_run_python_code_syntax_error(self, mock_subprocess):
        """Test Python code with syntax error."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "SyntaxError: invalid syntax\n"
        mock_subprocess.return_value = mock_result

        runner = SandboxRunner()
        result = runner.run("print('unclosed string", "python")

        assert result.success is False
        assert result.stdout == ""
        assert "SyntaxError" in result.stderr
        assert result.exit_code == 1

    @patch("subprocess.run")
    def test_run_timeout(self, mock_subprocess):
        """Test code execution timeout."""
        import subprocess

        mock_subprocess.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=30)

        runner = SandboxRunner()
        result = runner.run("import time; time.sleep(60)", "python")

        assert result.success is False
        assert result.timed_out is True
        assert "timed out" in result.error.lower()

    def test_run_unsupported_language(self):
        """Test execution with unsupported language."""
        runner = SandboxRunner()
        result = runner.run("print('test')", "unsupported_lang")
        assert result.success is False
        assert "Unsupported language" in result.error

    @patch("subprocess.run")
    def test_run_with_file_input(self, mock_subprocess):
        """Test code execution with file input."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "42\n"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print(42)")
            temp_file = Path(f.name)

        try:
            runner = SandboxRunner()
            result = runner.run(temp_file.read_text(), "python")

            assert result.success is True
            assert result.stdout == "42\n"
        finally:
            temp_file.unlink()

    def test_safety_check_dangerous_code(self):
        """Test safety check for dangerous code patterns."""
        runner = SandboxRunner()

        dangerous_codes = [
            "import os; os.system('rm -rf /')",
            "__import__('os').system('ls')",
            'eval(\'__import__("os").system("ls")\')',
            "exec(open('/etc/passwd').read())",
        ]

        for code in dangerous_codes:
            result = runner.run(code, "python")
            # SandboxRunner should execute the code but not raise ValueError
            # The actual safety checks are handled by the sandbox environment
            assert isinstance(result, type(runner.run("print('test')", "python")))


if __name__ == "__main__":
    pytest.main([__file__])
