"""Lint validator using ruff."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import List

from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult


class LintValidator:
    """Validator for linting issues using ruff."""

    tier = 1
    weight = 0.5  # Lower weight as linting is less critical

    def __init__(self, settings=None):
        """Initialize lint validator."""
        self.settings = settings

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate code for linting issues using ruff.

        Args:
            proposal: Code proposal to validate
            context: Additional context

        Returns:
            ValidationResult with linting issues
        """
        if proposal.language != "python":
            # Only supports Python for now
            return ValidationResult(
                validator="lint",
                score=1.0,
                weight=self.weight,
                issues=[],
                details={"language": proposal.language, "supported": False},
            )

        issues = self._check_ruff(proposal.code)

        return ValidationResult(
            validator="lint",
            score=1.0 - len(issues) / 20,  # Simple scoring
            weight=self.weight,
            issues=issues,
            details={"issue_count": len(issues), "tool": "ruff"},
        )

    def _check_ruff(self, code: str) -> List[Issue]:
        """Check code with ruff and return issues.

        Args:
            code: Python code to check

        Returns:
            List of validation issues
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = f.name

            # Run ruff with JSON output
            result = subprocess.run(
                ["ruff", "check", "--format=json", temp_file], capture_output=True, text=True
            )

            # Clean up
            Path(temp_file).unlink()

            issues = []
            if result.stdout:
                try:
                    ruff_results = json.loads(result.stdout)
                    for item in ruff_results:
                        issue = self._parse_ruff_result(item)
                        if issue:
                            issues.append(issue)
                except json.JSONDecodeError:
                    # Fallback to text parsing
                    issues = self._parse_ruff_text(result.stdout)

            return issues

        except (subprocess.SubprocessError, FileNotFoundError):
            # ruff not available or other error
            return []

    def _parse_ruff_result(self, item: dict) -> Issue:
        """Parse a ruff JSON result into an Issue.

        Args:
            item: Ruff result dictionary

        Returns:
            Issue object
        """
        # Determine severity based on ruff rule type
        severity = Severity.ERROR
        if any(
            item.get("code", "").startswith(prefix)
            for prefix in [
                "F",
                "E",
                "W",  # Flake8, pycodestyle warnings
            ]
        ):
            severity = Severity.WARNING
        elif item.get("code", "").startswith("B"):
            severity = Severity.WARNING  # Bugbear is often warning

        return Issue(
            message=item.get("message", ""),
            severity=severity,
            line=item.get("location", {}).get("row", 1),
            column=item.get("location", {}).get("column", 0),
            rule=f"ruff.{item.get('code', 'unknown')}",
            end_line=item.get("end_location", {}).get("row"),
            end_column=item.get("end_location", {}).get("column"),
        )

    def _parse_ruff_text(self, output: str) -> List[Issue]:
        """Parse ruff text output as fallback.

        Args:
            output: Ruff text output

        Returns:
            List of Issue objects
        """
        issues = []
        for line in output.strip().split("\n"):
            if line.strip():
                # Example: file.py:5:1: E401 Multiple imports on one line
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    _, line_num, col_num, message = parts
                    try:
                        line_num = int(line_num)
                        col_num = int(col_num)

                        # Extract rule code
                        rule = "ruff.unknown"
                        if " " in message:
                            potential_code = message.split()[0]
                            if len(potential_code) <= 10 and potential_code.isalnum():
                                rule = f"ruff.{potential_code}"

                        severity = Severity.WARNING
                        if message.startswith("E"):
                            severity = Severity.ERROR

                        issues.append(
                            Issue(
                                message=message.strip(),
                                severity=severity,
                                line=line_num,
                                column=col_num,
                                rule=rule,
                            )
                        )
                    except ValueError:
                        continue

        return issues


def create_validator(settings=None) -> LintValidator:
    """Factory function for LintValidator.

    Args:
        settings: Optional settings

    Returns:
        LintValidator instance
    """
    return LintValidator(settings)
