"""Tests for the scoring engine."""

from vallm.config import VallmSettings
from vallm.scoring import (
    Issue,
    PipelineResult,
    Severity,
    ValidationResult,
    Verdict,
    compute_verdict,
)


def test_verdict_pass():
    results = [
        ValidationResult(validator="test", score=0.9, weight=1.0),
    ]
    pipeline = compute_verdict(results)
    assert pipeline.verdict == Verdict.PASS


def test_verdict_review():
    results = [
        ValidationResult(validator="test", score=0.6, weight=1.0),
    ]
    pipeline = compute_verdict(results)
    assert pipeline.verdict == Verdict.REVIEW


def test_verdict_fail():
    results = [
        ValidationResult(validator="test", score=0.3, weight=1.0),
    ]
    pipeline = compute_verdict(results)
    assert pipeline.verdict == Verdict.FAIL


def test_hard_gate_on_error():
    results = [
        ValidationResult(
            validator="test",
            score=0.95,
            weight=1.0,
            issues=[Issue(message="critical", severity=Severity.ERROR)],
        ),
    ]
    pipeline = compute_verdict(results)
    assert pipeline.verdict == Verdict.FAIL


def test_weighted_score():
    results = [
        ValidationResult(validator="a", score=1.0, weight=2.0),
        ValidationResult(validator="b", score=0.0, weight=1.0),
    ]
    pipeline = PipelineResult(results=results)
    # weighted = (1.0*2.0 + 0.0*1.0) / (2.0 + 1.0) = 0.667
    assert abs(pipeline.weighted_score - 2 / 3) < 0.01


def test_custom_thresholds():
    settings = VallmSettings(pass_threshold=0.9, review_threshold=0.7)
    results = [
        ValidationResult(validator="test", score=0.85, weight=1.0),
    ]
    pipeline = compute_verdict(results, settings)
    assert pipeline.verdict == Verdict.REVIEW
