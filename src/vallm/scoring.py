"""Weighted scoring and verdict engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from vallm.config import VallmSettings
from vallm.core.proposal import Proposal


class Verdict(Enum):
    PASS = "pass"
    REVIEW = "review"
    FAIL = "fail"


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    """A single issue found during validation."""

    message: str
    severity: Severity = Severity.WARNING
    line: Optional[int] = None
    column: Optional[int] = None
    rule: Optional[str] = None

    def __str__(self) -> str:
        loc = ""
        if self.line is not None:
            loc = f":{self.line}"
            if self.column is not None:
                loc += f":{self.column}"
        return f"[{self.severity.value}]{loc} {self.message}"


@dataclass
class ValidationResult:
    """Result from a single validator."""

    validator: str
    score: float  # 0.0–1.0
    weight: float = 1.0  # configurable importance
    confidence: float = 1.0  # validator's self-assessed confidence
    issues: list[Issue] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight * self.confidence

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)


@dataclass
class PipelineResult:
    """Aggregated result from all validators."""

    results: list[ValidationResult] = field(default_factory=list)
    verdict: Verdict = Verdict.FAIL

    @property
    def weighted_score(self) -> float:
        if not self.results:
            return 0.0
        total_weight = sum(r.weight * r.confidence for r in self.results)
        if total_weight == 0:
            return 0.0
        return sum(r.weighted_score for r in self.results) / total_weight

    @property
    def all_issues(self) -> list[Issue]:
        issues = []
        for r in self.results:
            issues.extend(r.issues)
        return issues

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.all_issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.all_issues if i.severity == Severity.WARNING)


def compute_verdict(
    results: list[ValidationResult],
    settings: Optional[VallmSettings] = None,
) -> PipelineResult:
    """Compute the aggregate verdict from a list of validation results."""
    if settings is None:
        settings = VallmSettings()

    pipeline = PipelineResult(results=results)

    # Hard gate: any error-severity issue → FAIL
    if any(r.has_errors for r in results):
        pipeline.verdict = Verdict.FAIL
        return pipeline

    score = pipeline.weighted_score
    if score >= settings.pass_threshold:
        pipeline.verdict = Verdict.PASS
    elif score >= settings.review_threshold:
        pipeline.verdict = Verdict.REVIEW
    else:
        pipeline.verdict = Verdict.FAIL

    return pipeline


def validate(
    proposal: Proposal,
    settings: Optional[VallmSettings] = None,
    validators: Optional[list] = None,
    context: Optional[dict] = None,
) -> PipelineResult:
    """Run the full validation pipeline on a proposal.

    Args:
        proposal: The code proposal to validate.
        settings: Optional settings override.
        validators: Optional list of validator instances. If None, uses defaults.
        context: Optional additional context dict passed to validators.

    Returns:
        PipelineResult with verdict and all validation results.
    """
    if settings is None:
        settings = VallmSettings()
    if context is None:
        context = {}

    if validators is None:
        validators = _get_default_validators(settings)

    # Sort validators by tier for fail-fast behavior
    validators.sort(key=lambda v: v.tier)

    results = []
    for validator in validators:
        result = validator.validate(proposal, context)
        results.append(result)

        # Fail fast on errors in tier 1
        if result.has_errors and validator.tier == 1:
            return compute_verdict(results, settings)

    return compute_verdict(results, settings)


def _get_default_validators(settings: VallmSettings) -> list:
    """Build the default validator list based on settings."""
    validators = []

    if settings.enable_syntax:
        from vallm.validators.syntax import SyntaxValidator

        validators.append(SyntaxValidator())

    if settings.enable_imports:
        from vallm.validators.imports import ImportValidator

        validators.append(ImportValidator())

    if settings.enable_complexity:
        from vallm.validators.complexity import ComplexityValidator

        validators.append(ComplexityValidator(settings))

    if settings.enable_security:
        from vallm.validators.security import SecurityValidator

        validators.append(SecurityValidator())

    if settings.enable_semantic:
        from vallm.validators.semantic import SemanticValidator

        validators.append(SemanticValidator(settings))

    return validators
