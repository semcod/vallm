"""Regression validator: runs pytest against the proposed code and reports results."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator


class RegressionValidator(BaseValidator):
    """Tier 2: Run pytest against proposed code and report pass/fail.

    The validator writes the proposed code to a temporary file, then runs
    pytest in a subprocess.  If a ``test_dir`` is provided in the proposal
    metadata or the validator constructor, that directory is used as the
    test root; otherwise the validator looks for a ``tests/`` directory
    relative to the current working directory.

    Scoring
    -------
    * All tests pass  → 1.0
    * Some tests fail → 0.0  (with ERROR-severity issues for each failure)
    * No tests found  → 0.8  (neutral; not a hard failure)
    * pytest crashes  → 0.0  (ERROR issue with stderr)
    """

    tier: int = 2
    name: str = "regression"

    # pytest exit codes
    _EC_OK = 0
    _EC_TESTS_FAILED = 1
    _EC_INTERRUPTED = 2
    _EC_INTERNAL_ERROR = 3
    _EC_USAGE_ERROR = 4
    _EC_NO_TESTS = 5

    def __init__(
        self,
        test_dir: Optional[Path | str] = None,
        timeout: int = 120,
        extra_args: Optional[list[str]] = None,
    ) -> None:
        """
        Args:
            test_dir: Directory containing tests.  Defaults to ``tests/``
                      relative to cwd, or whatever is found in
                      ``proposal.metadata["test_dir"]`` at runtime.
            timeout: Maximum seconds to allow pytest to run.
            extra_args: Additional arguments forwarded to pytest.
        """
        self.test_dir = Path(test_dir) if test_dir else None
        self.timeout = timeout
        self.extra_args = extra_args or []

    # ------------------------------------------------------------------
    # BaseValidator interface
    # ------------------------------------------------------------------

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:  # noqa: D102
        test_dir = self._resolve_test_dir(proposal)

        with tempfile.TemporaryDirectory() as tmp:
            code_path = self._write_code(proposal, Path(tmp))
            return self._run_pytest(code_path, test_dir, proposal)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_test_dir(self, proposal: Proposal) -> Optional[Path]:
        """Return the test directory to use, or None if not found."""
        # 1. Constructor argument wins.
        if self.test_dir is not None:
            return self.test_dir

        # 2. Proposal metadata.
        meta_dir = (proposal.metadata or {}).get("test_dir")
        if meta_dir:
            return Path(meta_dir)

        # 3. Conventional ``tests/`` next to cwd.
        candidate = Path.cwd() / "tests"
        if candidate.is_dir():
            return candidate

        return None

    def _write_code(self, proposal: Proposal, tmp_dir: Path) -> Path:
        """Write proposal code to a temp file and return its path."""
        filename = proposal.filename or "proposed_code.py"
        # Strip any directory component so we always write into tmp_dir.
        code_path = tmp_dir / Path(filename).name
        code_path.write_text(proposal.code, encoding="utf-8")
        return code_path

    def _build_pytest_cmd(
        self,
        code_path: Path,
        test_dir: Optional[Path],
    ) -> list[str]:
        """Assemble the pytest command."""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--tb=short",
            "--no-header",
            "-q",
        ]
        cmd.extend(self.extra_args)

        if test_dir is not None:
            cmd.append(str(test_dir))

        return cmd

    def _run_pytest(
        self,
        code_path: Path,
        test_dir: Optional[Path],
        proposal: Proposal,
    ) -> ValidationResult:
        """Execute pytest and convert the outcome to a ValidationResult."""
        cmd = self._build_pytest_cmd(code_path, test_dir)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return self._timeout_result()
        except Exception as exc:  # pragma: no cover
            return self._exception_result(exc)

        return self._interpret(proc)

    def _interpret(self, proc: subprocess.CompletedProcess) -> ValidationResult:
        """Map a completed pytest process to a ValidationResult."""
        ec = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        output = (stdout + "\n" + stderr).strip()

        if ec == self._EC_OK:
            return ValidationResult(
                validator=self.name,
                score=1.0,
                details={"pytest_output": output, "exit_code": ec},
            )

        if ec == self._EC_NO_TESTS:
            return ValidationResult(
                validator=self.name,
                score=0.8,
                issues=[
                    Issue(
                        message="No tests were collected by pytest.",
                        severity=Severity.WARNING,
                        rule="regression/no-tests",
                    )
                ],
                details={"pytest_output": output, "exit_code": ec},
            )

        if ec == self._EC_TESTS_FAILED:
            issues = self._parse_failures(stdout)
            if not issues:
                # Fallback: surface raw output as a single issue.
                issues = [
                    Issue(
                        message=f"pytest reported test failures.\n{output}",
                        severity=Severity.ERROR,
                        rule="regression/test-failed",
                    )
                ]
            return ValidationResult(
                validator=self.name,
                score=0.0,
                issues=issues,
                details={"pytest_output": output, "exit_code": ec},
            )

        # Any other non-zero exit (interrupted, internal error, usage error …)
        return ValidationResult(
            validator=self.name,
            score=0.0,
            issues=[
                Issue(
                    message=(f"pytest exited with code {ec}.\n{output}"),
                    severity=Severity.ERROR,
                    rule="regression/pytest-error",
                )
            ],
            details={"pytest_output": output, "exit_code": ec},
        )

    # ------------------------------------------------------------------
    # Failure parsing
    # ------------------------------------------------------------------

    def _parse_failures(self, stdout: str) -> list[Issue]:
        """Extract individual FAILED lines from pytest -q output."""
        issues: list[Issue] = []
        for line in stdout.splitlines():
            stripped = line.strip()
            if stripped.startswith("FAILED "):
                test_id = stripped[len("FAILED ") :].strip()
                # Remove trailing " - AssertionError: …" style suffix for the
                # rule field; keep the full text in the message.
                issues.append(
                    Issue(
                        message=f"Test failed: {test_id}",
                        severity=Severity.ERROR,
                        rule="regression/test-failed",
                    )
                )
        return issues

    # ------------------------------------------------------------------
    # Error helpers
    # ------------------------------------------------------------------

    def _timeout_result(self) -> ValidationResult:
        return ValidationResult(
            validator=self.name,
            score=0.0,
            issues=[
                Issue(
                    message=(f"pytest timed out after {self.timeout} seconds."),
                    severity=Severity.ERROR,
                    rule="regression/timeout",
                )
            ],
            details={"exit_code": None},
        )

    def _exception_result(self, exc: Exception) -> ValidationResult:
        return ValidationResult(
            validator=self.name,
            score=0.0,
            issues=[
                Issue(
                    message=f"Failed to launch pytest: {exc}",
                    severity=Severity.ERROR,
                    rule="regression/launch-error",
                )
            ],
            details={"exit_code": None},
        )
