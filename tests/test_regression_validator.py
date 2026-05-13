"""Tests for RegressionValidator."""

from __future__ import annotations

import subprocess
from typing import Optional
from unittest.mock import patch


from vallm.core.proposal import Proposal
from vallm.scoring import Severity
from vallm.validators.regression import RegressionValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_proposal(
    code: str = "x = 1",
    filename: Optional[str] = "proposed.py",
    metadata: Optional[dict] = None,
) -> Proposal:
    return Proposal(
        code=code,
        language="python",
        filename=filename,
        metadata=metadata or {},
    )


def _completed(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=["pytest"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


# ---------------------------------------------------------------------------
# Unit tests — _interpret
# ---------------------------------------------------------------------------


class TestInterpret:
    """Tests for RegressionValidator._interpret (pure logic, no subprocess)."""

    def setup_method(self):
        self.validator = RegressionValidator()

    def test_all_tests_pass(self):
        result = self.validator._interpret(_completed(0, stdout="3 passed"))
        assert result.score == 1.0
        assert result.issues == []
        assert result.details["exit_code"] == 0

    def test_no_tests_collected(self):
        result = self.validator._interpret(_completed(5, stdout="no tests ran"))
        assert result.score == 0.8
        assert len(result.issues) == 1
        assert result.issues[0].severity == Severity.WARNING
        assert result.issues[0].rule == "regression/no-tests"

    def test_tests_failed_with_failed_lines(self):
        stdout = (
            "FAILED tests/test_foo.py::test_bar - AssertionError: 1 != 2\n"
            "FAILED tests/test_foo.py::test_baz - AssertionError: boom\n"
            "2 failed, 1 passed\n"
        )
        result = self.validator._interpret(_completed(1, stdout=stdout))
        assert result.score == 0.0
        assert len(result.issues) == 2
        for issue in result.issues:
            assert issue.severity == Severity.ERROR
            assert issue.rule == "regression/test-failed"

    def test_tests_failed_no_failed_lines(self):
        """Fallback: no FAILED lines parsed → single generic error issue."""
        result = self.validator._interpret(_completed(1, stdout="something went wrong"))
        assert result.score == 0.0
        assert len(result.issues) == 1
        assert result.issues[0].severity == Severity.ERROR

    def test_pytest_internal_error(self):
        result = self.validator._interpret(_completed(3, stderr="internal error"))
        assert result.score == 0.0
        assert result.issues[0].severity == Severity.ERROR
        assert result.issues[0].rule == "regression/pytest-error"

    def test_pytest_usage_error(self):
        result = self.validator._interpret(_completed(4, stderr="usage error"))
        assert result.score == 0.0
        assert result.issues[0].rule == "regression/pytest-error"

    def test_pytest_interrupted(self):
        result = self.validator._interpret(_completed(2, stderr="interrupted"))
        assert result.score == 0.0
        assert result.issues[0].rule == "regression/pytest-error"


# ---------------------------------------------------------------------------
# Unit tests — _parse_failures
# ---------------------------------------------------------------------------


class TestParseFailures:
    def setup_method(self):
        self.validator = RegressionValidator()

    def test_parses_multiple_failed_lines(self):
        stdout = (
            "FAILED tests/test_a.py::test_one - AssertionError\n"
            "FAILED tests/test_b.py::test_two - ValueError: bad\n"
        )
        issues = self.validator._parse_failures(stdout)
        assert len(issues) == 2
        assert "test_one" in issues[0].message
        assert "test_two" in issues[1].message

    def test_ignores_non_failed_lines(self):
        stdout = "passed 5\nwarning: something\n"
        issues = self.validator._parse_failures(stdout)
        assert issues == []

    def test_empty_stdout(self):
        assert self.validator._parse_failures("") == []


# ---------------------------------------------------------------------------
# Unit tests — _resolve_test_dir
# ---------------------------------------------------------------------------


class TestResolveTestDir:
    def test_constructor_arg_wins(self, tmp_path):
        validator = RegressionValidator(test_dir=tmp_path)
        proposal = _make_proposal()
        assert validator._resolve_test_dir(proposal) == tmp_path

    def test_metadata_used_when_no_constructor_arg(self, tmp_path):
        validator = RegressionValidator()
        proposal = _make_proposal(metadata={"test_dir": str(tmp_path)})
        assert validator._resolve_test_dir(proposal) == tmp_path

    def test_falls_back_to_cwd_tests(self, tmp_path, monkeypatch):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        validator = RegressionValidator()
        proposal = _make_proposal()
        assert validator._resolve_test_dir(proposal) == tests_dir

    def test_returns_none_when_nothing_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        validator = RegressionValidator()
        proposal = _make_proposal()
        assert validator._resolve_test_dir(proposal) is None


# ---------------------------------------------------------------------------
# Unit tests — timeout / exception helpers
# ---------------------------------------------------------------------------


class TestErrorHelpers:
    def setup_method(self):
        self.validator = RegressionValidator(timeout=30)

    def test_timeout_result(self):
        result = self.validator._timeout_result()
        assert result.score == 0.0
        assert result.issues[0].rule == "regression/timeout"
        assert "30" in result.issues[0].message

    def test_exception_result(self):
        result = self.validator._exception_result(FileNotFoundError("pytest not found"))
        assert result.score == 0.0
        assert result.issues[0].rule == "regression/launch-error"
        assert "pytest not found" in result.issues[0].message


# ---------------------------------------------------------------------------
# Integration-style tests — validate() with mocked subprocess
# ---------------------------------------------------------------------------


class TestValidate:
    """Tests for the full validate() path with subprocess mocked out."""

    @patch("vallm.validators.regression.subprocess.run")
    def test_validate_passes(self, mock_run, tmp_path):
        mock_run.return_value = _completed(0, stdout="1 passed")
        validator = RegressionValidator(test_dir=tmp_path)
        result = validator.validate(_make_proposal(), {})
        assert result.score == 1.0
        assert result.validator == "regression"

    @patch("vallm.validators.regression.subprocess.run")
    def test_validate_fails(self, mock_run, tmp_path):
        stdout = "FAILED tests/test_x.py::test_y - AssertionError\n1 failed\n"
        mock_run.return_value = _completed(1, stdout=stdout)
        validator = RegressionValidator(test_dir=tmp_path)
        result = validator.validate(_make_proposal(), {})
        assert result.score == 0.0
        assert result.has_errors

    @patch("vallm.validators.regression.subprocess.run")
    def test_validate_no_tests(self, mock_run, tmp_path):
        mock_run.return_value = _completed(5)
        validator = RegressionValidator(test_dir=tmp_path)
        result = validator.validate(_make_proposal(), {})
        assert result.score == 0.8
        assert not result.has_errors

    @patch(
        "vallm.validators.regression.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="pytest", timeout=5),
    )
    def test_validate_timeout(self, mock_run, tmp_path):
        validator = RegressionValidator(test_dir=tmp_path, timeout=5)
        result = validator.validate(_make_proposal(), {})
        assert result.score == 0.0
        assert result.issues[0].rule == "regression/timeout"

    @patch("vallm.validators.regression.subprocess.run")
    def test_cmd_includes_extra_args(self, mock_run, tmp_path):
        mock_run.return_value = _completed(0)
        validator = RegressionValidator(test_dir=tmp_path, extra_args=["--maxfail=1", "-x"])
        validator.validate(_make_proposal(), {})
        called_cmd = mock_run.call_args[0][0]
        assert "--maxfail=1" in called_cmd
        assert "-x" in called_cmd

    @patch("vallm.validators.regression.subprocess.run")
    def test_cmd_includes_test_dir(self, mock_run, tmp_path):
        mock_run.return_value = _completed(0)
        validator = RegressionValidator(test_dir=tmp_path)
        validator.validate(_make_proposal(), {})
        called_cmd = mock_run.call_args[0][0]
        assert str(tmp_path) in called_cmd

    @patch("vallm.validators.regression.subprocess.run")
    def test_validator_name(self, mock_run, tmp_path):
        mock_run.return_value = _completed(0)
        validator = RegressionValidator(test_dir=tmp_path)
        result = validator.validate(_make_proposal(), {})
        assert result.validator == "regression"

    @patch("vallm.validators.regression.subprocess.run")
    def test_validator_tier(self, mock_run):
        validator = RegressionValidator()
        assert validator.tier == 2
