"""Intract intent contract validator for vallm."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from vallm.config import VallmSettings
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator


class IntractValidator(BaseValidator):
    """Validate @intract contracts in proposals using Intract."""

    tier = 2
    name = "intract"
    weight = 1.5

    def __init__(self, settings: Optional[VallmSettings] = None):
        self.settings = settings or VallmSettings()

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        try:
            from intract.integrations.vallm import validate_proposal
        except ImportError:
            return ValidationResult(
                validator=self.name,
                score=1.0,
                weight=self.weight,
                confidence=1.0,
                issues=[
                    Issue(
                        message="Intract is not installed. Install with: pip install 'vallm[intract]'",
                        severity=Severity.INFO,
                        rule="intract.missing",
                    )
                ],
                details={"skipped": True},
            )

        filename = proposal.filename or context.get("filename")
        mapped = validate_proposal(proposal.code, filename=filename)

        issues = [
            Issue(
                message=issue.message,
                severity=_map_severity(issue.severity),
                line=issue.line,
                rule=issue.rule,
            )
            for issue in mapped.issues
        ]

        return ValidationResult(
            validator=self.name,
            score=mapped.score,
            weight=self.weight,
            confidence=1.0,
            issues=issues,
            details={"status": mapped.status},
        )


def _map_severity(value: str) -> Severity:
    if value == "error":
        return Severity.ERROR
    if value == "warning":
        return Severity.WARNING
    return Severity.INFO


def run_project_intract_check(
    root: Path,
    *,
    staged: bool = False,
    changed: bool = False,
    base_ref: str = "main",
    manifest: Path | None = None,
):
    """Run project-level Intract validation for the vallm intract command."""
    from intract.check import changed_check, staged_check
    from intract.config import load_config
    from intract.policy import decide_policy
    from intract.project import validate_project

    config = load_config(root)
    manifest_path = manifest
    if manifest_path is None and (root / config.manifest).exists():
        manifest_path = root / config.manifest

    files: list[str] = []
    if staged:
        report, files, _hunks = staged_check(root, manifest=manifest_path)
        report.project_path = str(root)
    elif changed:
        report, files = changed_check(root, base_ref=base_ref, manifest=manifest_path)
        report.project_path = str(root)
    else:
        report = validate_project(root, manifest_path=manifest_path)

    decision = decide_policy(report, fail_on=config.fail_on, warn_on=config.warn_on)
    return report, decision, files
