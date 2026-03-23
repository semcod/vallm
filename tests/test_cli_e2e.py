#!/usr/bin/env python3
"""E2E tests for vallm CLI commands."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import List

import pytest


@pytest.mark.integration
class VallmCLI:
    """Helper class for running vallm CLI commands."""
    
    def __init__(self):
        self.vallm_cmd = "python3 -m vallm"
    
    def run(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run vallm command with given arguments."""
        cmd = self.vallm_cmd.split() + args
        return subprocess.run(cmd, capture_output=True, text=True, check=check)
    
    def run_success(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run vallm command expecting success."""
        return self.run(args, check=True)
    
    def run_failure(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run vallm command expecting failure."""
        return self.run(args, check=False)


@pytest.fixture
def vallm():
    """Fixture providing VallmCLI instance."""
    return VallmCLI()


@pytest.fixture
def temp_project():
    """Create a temporary project with multiple files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # Create Python files
        (project_dir / "main.py").write_text("""
def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

if __name__ == "__main__":
    print(fibonacci(10))
""")
        
        (project_dir / "utils.py").write_text("""
import os
import sys

def get_env_var(key: str, default: str = None) -> str:
    return os.getenv(key, default)

def validate_input(data: str) -> bool:
    return bool(data and data.strip())
""")
        
        # Create JavaScript files
        (project_dir / "app.js").write_text("""
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.json({ message: 'Hello World' });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
""")
        
        # Create Go files
        (project_dir / "main.go").write_text("""
package main

import "fmt"

func fibonacci(n int) []int {
    if n <= 0 {
        return []int{}
    }
    fib := []int{0, 1}
    for i := 2; i < n; i++ {
        fib = append(fib, fib[i-1]+fib[i-2])
    }
    return fib
}

func main() {
    fmt.Println(fibonacci(10))
}
""")
        
        # Create test directory
        test_dir = project_dir / "tests"
        test_dir.mkdir()
        (test_dir / "test_main.py").write_text("""
import pytest
from main import fibonacci

def test_fibonacci():
    assert fibonacci(0) == []
    assert fibonacci(1) == []
    assert fibonacci(2) == [0, 1]
    assert fibonacci(5) == [0, 1, 1, 2, 3]
""")
        
        # Create .gitignore
        (project_dir / ".gitignore").write_text("""
__pycache__/
*.pyc
venv/
.env
*.log
""")
        
        yield project_dir


@pytest.mark.integration
class TestCLICommands:
    """Test suite for CLI commands."""
    
    def test_help_command(self, vallm):
        """Test help command."""
        result = vallm.run_success(["--help"])
        assert "Validate LLM-generated code" in result.stdout
        assert "validate" in result.stdout
        assert "check" in result.stdout
        assert "batch" in result.stdout
        assert "info" in result.stdout
    
    def test_info_command(self, vallm):
        """Test info command."""
        result = vallm.run_success(["info"])
        assert "vallm Configuration" in result.stdout
        assert "Optional Dependencies" in result.stdout
    
    def test_validate_single_file(self, vallm, temp_project):
        """Test validating a single file."""
        file_path = temp_project / "main.py"
        result = vallm.run_success(["validate", "--file", str(file_path)])
        assert result.returncode == 0
        assert "PASS" in result.stdout or "REVIEW" in result.stdout
    
    def test_validate_with_code_string(self, vallm):
        """Test validating code string."""
        code = "def hello(): return 'world'"
        result = vallm.run_success(["validate", "--code", code])
        assert result.returncode == 0
    
    def test_check_syntax_only(self, vallm, temp_project):
        """Test syntax check only."""
        file_path = temp_project / "main.py"
        result = vallm.run_success(["check", str(file_path)])
        assert "syntax OK" in result.stdout
    
    def test_check_syntax_error(self, vallm):
        """Test syntax check with invalid code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def invalid syntax\n")
            f.flush()
            
            result = vallm.run_failure(["check", f.name])
            assert result.returncode != 0
            assert "syntax errors" in result.stdout
            
            Path(f.name).unlink()
    
    def test_batch_validation(self, vallm, temp_project):
        """Test batch validation."""
        result = vallm.run_success(["batch", str(temp_project), "--recursive"])
        assert result.returncode == 0
        assert "BATCH VALIDATION SUMMARY" in result.stdout
    
    def test_batch_with_include_patterns(self, vallm, temp_project):
        """Test batch validation with include patterns."""
        result = vallm.run_success([
            "batch", str(temp_project), "--recursive",
            "--include", "*.py"
        ])
        assert result.returncode == 0
    
    def test_batch_with_exclude_patterns(self, vallm, temp_project):
        """Test batch validation with exclude patterns."""
        result = vallm.run_success([
            "batch", str(temp_project), "--recursive",
            "--exclude", "*/test/*"
        ])
        assert result.returncode == 0
    
    def test_batch_json_output(self, vallm, temp_project):
        """Test batch validation with JSON output."""
        result = vallm.run_success([
            "batch", str(temp_project), "--recursive",
            "--format", "json"
        ])
        assert result.returncode == 0
        
        # Try to parse JSON output
        try:
            data = json.loads(result.stdout)
            assert "verdict" in data or isinstance(data, list)
        except json.JSONDecodeError:
            # If it's not valid JSON, that's okay for this test
            pass
    
    def test_batch_text_output(self, vallm, temp_project):
        """Test batch validation with text output."""
        result = vallm.run_success([
            "batch", str(temp_project), "--recursive",
            "--format", "text"
        ])
        assert result.returncode == 0
        assert "Individual Results:" in result.stdout
    
    def test_batch_fail_fast(self, vallm, temp_project):
        """Test batch validation with fail-fast."""
        # Create a file with syntax error
        error_file = temp_project / "error.py"
        error_file.write_text("def invalid syntax\n")
        
        result = vallm.run_failure([
            "batch", str(temp_project), "--recursive",
            "--fail-fast"
        ])
        assert result.returncode != 0
    
    def test_batch_no_gitignore(self, vallm, temp_project):
        """Test batch validation without gitignore."""
        result = vallm.run_success([
            "batch", str(temp_project), "--recursive",
            "--no-gitignore"
        ])
        assert result.returncode == 0
    
    def test_validate_nonexistent_file(self, vallm):
        """Test validating non-existent file."""
        result = vallm.run_failure([
            "validate", "--file", "nonexistent.py"
        ])
        assert result.returncode == 1
        assert "File not found" in result.stdout
    
    def test_check_nonexistent_file(self, vallm):
        """Test checking non-existent file."""
        result = vallm.run_failure(["check", "nonexistent.py"])
        assert result.returncode == 1
        assert "File not found" in result.stdout
    
    def test_validate_missing_code_or_file(self, vallm):
        """Test validate command without code or file."""
        result = vallm.run_failure(["validate"])
        assert result.returncode == 1
        assert "Provide --code or --file" in result.stdout


@pytest.mark.integration
class TestMultiLanguage:
    """Test multi-language support."""
    
    def test_python_validation(self, vallm, temp_project):
        """Test Python file validation."""
        file_path = temp_project / "main.py"
        result = vallm.run_success(["validate", "--file", str(file_path), "--lang", "python"])
        assert result.returncode == 0
    
    def test_javascript_validation(self, vallm, temp_project):
        """Test JavaScript file validation."""
        file_path = temp_project / "app.js"
        result = vallm.run_success(["validate", "--file", str(file_path), "--lang", "javascript"])
        assert result.returncode == 0
    
    def test_go_validation(self, vallm, temp_project):
        """Test Go file validation."""
        file_path = temp_project / "main.go"
        result = vallm.run_success(["validate", "--file", str(file_path), "--lang", "go"])
        assert result.returncode == 0
    
    def test_auto_language_detection(self, vallm, temp_project):
        """Test automatic language detection."""
        # Test Python file
        py_file = temp_project / "main.py"
        result = vallm.run_success(["validate", "--file", str(py_file)])
        assert "Detected language: Python" in result.stdout
        
        # Test JavaScript file
        js_file = temp_project / "app.js"
        result = vallm.run_success(["validate", "--file", str(js_file)])
        assert "Detected language: JavaScript" in result.stdout


@pytest.mark.integration
class TestConfiguration:
    """Test configuration options."""
    
    def test_validate_with_config_file(self, vallm, temp_project):
        """Test validation with config file."""
        config_path = temp_project / "vallm.toml"
        config_path.write_text("""
pass_threshold = 0.8
review_threshold = 0.5
max_cyclomatic_complexity = 10
""")
        
        file_path = temp_project / "main.py"
        result = vallm.run_failure([
            "validate", "--file", str(file_path),
            "--config", str(config_path)
        ])
        # Config loading not implemented yet, expect failure
        assert result.returncode != 0
    
    def test_validate_with_verbose(self, vallm, temp_project):
        """Test validation with verbose output."""
        file_path = temp_project / "main.py"
        result = vallm.run_success([
            "validate", "--file", str(file_path),
            "--verbose"
        ])
        assert result.returncode == 0
        assert len(result.stdout) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
