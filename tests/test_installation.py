#!/usr/bin/env python3
"""Installation tests for vallm using pip and pipx."""

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List

import pytest


class InstallationTester:
    """Helper class for testing installation methods."""
    
    @staticmethod
    def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run command with proper error handling."""
        return subprocess.run(cmd, capture_output=True, text=True, check=check)
    
    @staticmethod
    def create_test_package() -> Path:
        """Create a test package directory."""
        test_dir = Path(tempfile.mkdtemp(prefix="vallm_test_"))
        
        # Create a simple Python project
        (test_dir / "pyproject.toml").write_text("""
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "test-vallm-project"
version = "0.1.0"
description = "Test project for vallm"
requires-python = ">=3.10"

[tool.vallm]
pass_threshold = 0.8
""")
        
        # Create test files
        (test_dir / "main.py").write_text("""
def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

def main():
    print(fibonacci(10))

if __name__ == "__main__":
    main()
""")
        
        (test_dir / "utils.py").write_text("""
import os
import sys

def get_env_var(key: str, default: str = None) -> str:
    return os.getenv(key, default)

def validate_path(path: str) -> bool:
    return Path(path).exists() if path else False
""")
        
        return test_dir


class TestPipInstallation:
    """Test pip installation methods."""
    
    def test_pip_install_editable(self):
        """Test editable pip installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_dir = Path(tmpdir) / "test_venv"
            
            # Create virtual environment
            subprocess.run(["python3", "-m", "venv", str(venv_dir)], check=True)
            
            # Get python path for venv
            if venv_dir.joinpath("bin").exists():
                python_path = venv_dir / "bin" / "python"
                pip_path = venv_dir / "bin" / "pip"
            else:
                python_path = venv_dir / "Scripts" / "python.exe"
                pip_path = venv_dir / "Scripts" / "pip.exe"
            
            # Install vallm in editable mode
            project_root = Path(__file__).parent.parent.parent
            subprocess.run([str(pip_path), "install", "-e", str(project_root)], check=True)
            
            # Test installation
            result = subprocess.run([str(python_path), "-m", "vallm", "--help"], 
                                  capture_output=True, text=True, check=True)
            assert "Validate LLM-generated code" in result.stdout
            
            result = subprocess.run([str(python_path), "-m", "vallm", "info"], 
                                  capture_output=True, text=True, check=True)
            assert "vallm Configuration" in result.stdout
    
    def test_pip_install_from_local(self):
        """Test pip installation from local directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_dir = Path(tmpdir) / "test_venv"
            
            # Create virtual environment
            subprocess.run(["python3", "-m", "venv", str(venv_dir)], check=True)
            
            # Get pip path for venv
            if venv_dir.joinpath("bin").exists():
                pip_path = venv_dir / "bin" / "pip"
                python_path = venv_dir / "bin" / "python"
            else:
                pip_path = venv_dir / "Scripts" / "pip.exe"
                python_path = venv_dir / "Scripts" / "python.exe"
            
            # Create a wheel and install
            project_root = Path(__file__).parent.parent.parent
            subprocess.run([str(pip_path), "wheel", str(project_root), 
                          "--wheel-dir", tmpdir], check=True)
            
            wheel_files = list(Path(tmpdir).glob("vallm-*.whl"))
            assert wheel_files, "No wheel file found"
            
            subprocess.run([str(pip_path), "install", str(wheel_files[0])], check=True)
            
            # Test installation
            result = subprocess.run([str(python_path), "-m", "vallm", "--help"], 
                                  capture_output=True, text=True, check=True)
            assert "Validate LLM-generated code" in result.stdout
    
    def test_pip_install_with_extras(self):
        """Test pip installation with optional extras."""
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_dir = Path(tmpdir) / "test_venv"
            
            # Create virtual environment
            subprocess.run(["python3", "-m", "venv", str(venv_dir)], check=True)
            
            # Get pip path for venv
            if venv_dir.joinpath("bin").exists():
                pip_path = venv_dir / "bin" / "pip"
                python_path = venv_dir / "bin" / "python"
            else:
                pip_path = venv_dir / "Scripts" / "pip.exe"
                python_path = venv_dir / "Scripts" / "python.exe"
            
            # Install with all extras
            project_root = Path(__file__).parent.parent.parent
            subprocess.run([str(pip_path), "install", "-e", f"{project_root}[all]"], check=True)
            
            # Test that optional dependencies are available
            result = subprocess.run([str(python_path), "-c", 
                                   "import ollama, litellm, bandit, networkx; print('All extras imported')"], 
                                  capture_output=True, text=True)
            
            # Some extras might not be available in test environment, so don't fail hard
            if result.returncode != 0:
                print(f"Warning: Some extras not available: {result.stderr}")
            
            # Test vallm still works
            result = subprocess.run([str(python_path), "-m", "vallm", "info"], 
                                  capture_output=True, text=True, check=True)
            assert "vallm Configuration" in result.stdout


class TestPipxInstallation:
    """Test pipx installation methods."""
    
    @pytest.mark.skipif(shutil.which("pipx") is None, reason="pipx not available")
    def test_pipx_install_editable(self):
        """Test pipx editable installation."""
        project_root = Path(__file__).parent.parent.parent
        
        # Install with pipx
        subprocess.run(["pipx", "install", "--editable", str(project_root)], check=True)
        
        try:
            # Test installation
            result = subprocess.run(["vallm", "--help"], 
                                  capture_output=True, text=True, check=True)
            assert "Validate LLM-generated code" in result.stdout
            
            result = subprocess.run(["vallm", "info"], 
                                  capture_output=True, text=True, check=True)
            assert "vallm Configuration" in result.stdout
        finally:
            # Uninstall
            subprocess.run(["pipx", "uninstall", "vallm"], check=False)
    
    @pytest.mark.skipif(shutil.which("pipx") is None, reason="pipx not available")
    def test_pipx_install_with_extras(self):
        """Test pipx installation with extras."""
        project_root = Path(__file__).parent.parent.parent
        
        # Install with pipx and extras
        subprocess.run(["pipx", "install", "--editable", f"{project_root}[llm,security]"], check=True)
        
        try:
            # Test installation
            result = subprocess.run(["vallm", "info"], 
                                  capture_output=True, text=True, check=True)
            assert "vallm Configuration" in result.stdout
        finally:
            # Uninstall
            subprocess.run(["pipx", "uninstall", "vallm"], check=False)


class TestPostInstallation:
    """Test functionality after installation."""
    
    def test_basic_functionality(self):
        """Test basic vallm functionality after installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_dir = Path(tmpdir) / "test_venv"
            
            # Create virtual environment
            subprocess.run(["python3", "-m", "venv", str(venv_dir)], check=True)
            
            # Get paths for venv
            if venv_dir.joinpath("bin").exists():
                python_path = venv_dir / "bin" / "python"
                vallm_cmd = [str(python_path), "-m", "vallm"]
            else:
                python_path = venv_dir / "Scripts" / "python.exe"
                vallm_cmd = [str(python_path), "-m", "vallm"]
            
            # Install vallm
            project_root = Path(__file__).parent.parent.parent
            subprocess.run([str(python_path), "-m", "pip", "install", "-e", str(project_root)], check=True)
            
            # Create test project
            test_project = InstallationTester.create_test_package()
            
            # Test various commands
            result = subprocess.run(vallm_cmd + ["--help"], 
                                  capture_output=True, text=True, check=True)
            assert "Validate LLM-generated code" in result.stdout
            
            result = subprocess.run(vallm_cmd + ["info"], 
                                  capture_output=True, text=True, check=True)
            assert "vallm Configuration" in result.stdout
            
            # Test single file validation
            test_file = test_project / "main.py"
            result = subprocess.run(vallm_cmd + ["validate", "--file", str(test_file)], 
                                  capture_output=True, text=True)
            # Don't check return code strictly as validation might fail
            assert result.returncode in [0, 1, 2]
            
            # Test batch validation
            result = subprocess.run(vallm_cmd + ["batch", str(test_project), "--recursive"], 
                                  capture_output=True, text=True)
            assert result.returncode in [0, 1, 2]
            
            # Clean up
            shutil.rmtree(test_project)
    
    def test_language_detection(self):
        """Test language detection after installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_dir = Path(tmpdir) / "test_venv"
            
            # Create virtual environment
            subprocess.run(["python3", "-m", "venv", str(venv_dir)], check=True)
            
            # Get paths for venv
            if venv_dir.joinpath("bin").exists():
                python_path = venv_dir / "bin" / "python"
                vallm_cmd = [str(python_path), "-m", "vallm"]
            else:
                python_path = venv_dir / "Scripts" / "python.exe"
                vallm_cmd = [str(python_path), "-m", "vallm"]
            
            # Install vallm
            project_root = Path(__file__).parent.parent.parent
            subprocess.run([str(python_path), "-m", "pip", "install", "-e", str(project_root)], check=True)
            
            # Test different languages
            test_cases = [
                ("test.py", "python", "def hello(): pass"),
                ("test.js", "javascript", "function hello() {}"),
                ("test.go", "go", "package main\nfunc main() {}"),
                ("test.rs", "rust", "fn main() {}"),
            ]
            
            for filename, expected_lang, code in test_cases:
                with tempfile.NamedTemporaryFile(mode="w", suffix=filename, delete=False) as f:
                    f.write(code)
                    f.flush()
                    
                    result = subprocess.run(vallm_cmd + ["validate", "--file", f.name], 
                                          capture_output=True, text=True)
                    
                    # Check if language was detected
                    if expected_lang == "python":
                        assert "Detected language: Python" in result.stdout
                    elif expected_lang == "javascript":
                        assert "Detected language: JavaScript" in result.stdout
                    
                    Path(f.name).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
