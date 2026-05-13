"""Tests for vallm examples in examples/ directory.

This module tests that all example scripts run without errors
and produce expected outputs.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Base directory for examples
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


@pytest.mark.slow
class TestBasicValidationExample:
    """Test 01_basic_validation example."""

    def test_example_runs_without_errors(self):
        """Verify the basic validation example executes successfully."""
        script_path = EXAMPLES_DIR / "01_basic_validation" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Script failed with: {result.stderr}"

    def test_good_code_passes(self):
        """Verify good code sample passes validation."""
        script_path = EXAMPLES_DIR / "01_basic_validation" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "good_code: pass" in result.stdout

    def test_bad_code_fails(self):
        """Verify bad code sample fails validation."""
        script_path = EXAMPLES_DIR / "01_basic_validation" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "bad_code: fail" in result.stdout

    def test_detects_syntax_error(self):
        """Verify syntax error is detected in bad code."""
        script_path = EXAMPLES_DIR / "01_basic_validation" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "SyntaxError" in result.stdout


@pytest.mark.slow
class TestAstComparisonExample:
    """Test 02_ast_comparison example."""

    def test_example_runs_without_errors(self):
        """Verify AST comparison example executes successfully."""
        script_path = EXAMPLES_DIR / "02_ast_comparison" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Script failed with: {result.stderr}"

    def test_calculates_similarity(self):
        """Verify AST similarity is calculated."""
        script_path = EXAMPLES_DIR / "02_ast_comparison" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "AST Similarity" in result.stdout

    def test_shows_node_counts(self):
        """Verify node counts are displayed for multiple languages."""
        script_path = EXAMPLES_DIR / "02_ast_comparison" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "nodes" in result.stdout
        assert "Python" in result.stdout

    def test_structural_diff_output(self):
        """Verify structural diff is generated."""
        script_path = EXAMPLES_DIR / "02_ast_comparison" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "Structural Diff" in result.stdout


@pytest.mark.slow
class TestSecurityCheckExample:
    """Test 03_security_check example."""

    def test_example_runs_without_errors(self):
        """Verify security check example executes successfully."""
        script_path = EXAMPLES_DIR / "03_security_check" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Script failed with: {result.stderr}"

    def test_detects_insecure_code(self):
        """Verify insecure code is flagged."""
        script_path = EXAMPLES_DIR / "03_security_check" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "Insecure code" in result.stdout or "INSECURE" in result.stdout
        assert result.stdout.count("eval()") > 0 or "security" in result.stdout.lower()

    def test_secure_code_passes(self):
        """Verify secure code passes validation."""
        script_path = EXAMPLES_DIR / "03_security_check" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "Secure code" in result.stdout or "SECURE" in result.stdout
        assert "1.00" in result.stdout or "score" in result.stdout.lower()


@pytest.mark.slow
class TestGraphAnalysisExample:
    """Test 04_graph_analysis example."""

    def test_example_runs_without_errors(self):
        """Verify graph analysis example executes successfully."""
        script_path = EXAMPLES_DIR / "04_graph_analysis" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Script failed with: {result.stderr}"

    def test_builds_call_graph(self):
        """Verify call graph is built and displayed."""
        script_path = EXAMPLES_DIR / "04_graph_analysis" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "Code Graph" in result.stdout
        assert "Imports:" in result.stdout
        assert "Functions:" in result.stdout

    def test_detects_changes(self):
        """Verify structural changes are detected."""
        script_path = EXAMPLES_DIR / "04_graph_analysis" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "Has changes" in result.stdout or "Changes detected" in result.stdout


@pytest.mark.slow
class TestMultiLanguageExample:
    """Test 07_multi_language example."""

    def test_example_runs_without_errors(self):
        """Verify multi-language example executes successfully."""
        script_path = EXAMPLES_DIR / "07_multi_language" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Script failed with: {result.stderr}"

    def test_shows_supported_languages(self):
        """Verify supported languages are listed."""
        script_path = EXAMPLES_DIR / "07_multi_language" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "languages supported" in result.stdout

    def test_validates_multiple_languages(self):
        """Verify multiple languages are validated."""
        script_path = EXAMPLES_DIR / "07_multi_language" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        # Check for some common languages
        languages = ["python", "javascript", "go", "rust", "java"]
        found_languages = sum(1 for lang in languages if lang in result.stdout.lower())
        assert found_languages >= 3, f"Expected at least 3 languages, found {found_languages}"


@pytest.mark.slow
class TestCode2llmIntegrationExample:
    """Test 08_code2llm_integration example."""

    def test_example_runs_without_errors(self):
        """Verify code2llm integration example executes successfully."""
        script_path = EXAMPLES_DIR / "08_code2llm_integration" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Script failed with: {result.stderr}"

    def test_validates_sample_project(self):
        """Verify sample project is created and validated."""
        script_path = EXAMPLES_DIR / "08_code2llm_integration" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "sample project" in result.stdout.lower() or "Validating" in result.stdout

    def test_generates_report(self):
        """Verify integration report is generated."""
        script_path = EXAMPLES_DIR / "08_code2llm_integration" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "Report" in result.stdout or "report" in result.stdout.lower()


@pytest.mark.slow
class TestCode2logicIntegrationExample:
    """Test 09_code2logic_integration example."""

    def test_example_runs_without_errors(self):
        """Verify code2logic integration example executes successfully."""
        script_path = EXAMPLES_DIR / "09_code2logic_integration" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Script failed with: {result.stderr}"

    def test_validates_code(self):
        """Verify code is validated."""
        script_path = EXAMPLES_DIR / "09_code2logic_integration" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "Verdict:" in result.stdout
        assert "Score:" in result.stdout

    def test_builds_call_graph(self):
        """Verify call graph is built."""
        script_path = EXAMPLES_DIR / "09_code2logic_integration" / "main.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        assert "call graph" in result.stdout.lower() or "Functions:" in result.stdout


@pytest.mark.slow
@pytest.mark.parametrize(
    "example_name,main_file",
    [
        ("01_basic_validation", "main.py"),
        ("02_ast_comparison", "main.py"),
        ("03_security_check", "main.py"),
        ("04_graph_analysis", "main.py"),
        ("07_multi_language", "main.py"),
        ("08_code2llm_integration", "main.py"),
        ("09_code2logic_integration", "main.py"),
    ],
)
def test_all_examples_exist(example_name, main_file):
    """Verify all expected example directories and files exist."""
    example_dir = EXAMPLES_DIR / example_name
    assert example_dir.exists(), f"Example directory missing: {example_name}"
    assert (example_dir / main_file).exists(), f"{main_file} missing in {example_name}"


@pytest.mark.slow
def test_examples_utils_exist():
    """Verify shared utilities exist."""
    utils_dir = EXAMPLES_DIR / "utils"
    assert utils_dir.exists(), "utils directory missing"
    assert (utils_dir / "__init__.py").exists(), "utils/__init__.py missing"
