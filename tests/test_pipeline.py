"""Tests for the full validation pipeline."""

from vallm import Proposal, VallmSettings, validate
from vallm.scoring import ValidationResult, Verdict


def test_pipeline_good_code():
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
        enable_semantic=False,
    )
    code = "def add(a: int, b: int) -> int:\n    return a + b"
    proposal = Proposal(code=code, language="python")
    result = validate(proposal, settings)
    assert result.verdict == Verdict.PASS


def test_pipeline_syntax_error():
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=False,
        enable_complexity=False,
        enable_security=False,
        enable_semantic=False,
    )
    code = "def foo(:\n  return"
    proposal = Proposal(code=code, language="python")
    result = validate(proposal, settings)
    assert result.verdict == Verdict.FAIL


def test_pipeline_missing_import():
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=False,
        enable_security=False,
        enable_semantic=False,
    )
    code = "import nonexistent_xyz_module"
    proposal = Proposal(code=code, language="python")
    result = validate(proposal, settings)
    # Import warning should lower score but not necessarily fail
    assert result.weighted_score < 1.0


def test_pipeline_includes_regression_validator(monkeypatch):
    class DummyRegressionValidator:
        tier = 2

        def validate(self, proposal, context):
            return ValidationResult(validator="regression", score=1.0)

    monkeypatch.setattr(
        "vallm.validators.regression.RegressionValidator",
        DummyRegressionValidator,
    )

    settings = VallmSettings(
        enable_syntax=False,
        enable_imports=False,
        enable_complexity=False,
        enable_security=False,
        enable_regression=True,
        enable_semantic=False,
    )
    proposal = Proposal(code="def add(a: int, b: int) -> int:\n    return a + b", language="python")
    result = validate(proposal, settings)
    assert [r.validator for r in result.results] == ["regression"]
    assert result.verdict == Verdict.PASS
