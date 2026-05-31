"""Tests for Intract validator integration."""

import sys
import types

import pytest

from vallm import Proposal, VallmSettings, validate
from vallm.scoring import Severity, ValidationResult, Verdict
from vallm.validators.intract import IntractValidator


def _install_fake_intract(monkeypatch, mapped_result):
    fake_vallm = types.ModuleType("intract.integrations.vallm")
    fake_vallm.validate_proposal = lambda code, filename=None: mapped_result
    fake_integrations = types.ModuleType("intract.integrations")
    fake_integrations.vallm = fake_vallm
    fake_intract = types.ModuleType("intract")
    fake_intract.integrations = fake_integrations

    monkeypatch.setitem(sys.modules, "intract", fake_intract)
    monkeypatch.setitem(sys.modules, "intract.integrations", fake_integrations)
    monkeypatch.setitem(sys.modules, "intract.integrations.vallm", fake_vallm)


def test_intract_validator_skips_when_no_contracts(monkeypatch):
    mapped = types.SimpleNamespace(score=1.0, status="pass", issues=())
    _install_fake_intract(monkeypatch, mapped)

    result = IntractValidator().validate(Proposal(code="def add(a, b): return a + b", language="python"), {})
    assert result.validator == "intract"
    assert result.score == 1.0
    assert not result.has_errors


def test_intract_validator_maps_violation(monkeypatch):
    issue = types.SimpleNamespace(
        rule="intract.contract",
        message="validate.user: violation; forbidden_effect",
        severity="error",
        line=2,
        filename="auth.py",
    )
    mapped = types.SimpleNamespace(score=0.0, status="violation", issues=(issue,))
    _install_fake_intract(monkeypatch, mapped)

    result = IntractValidator().validate(
        Proposal(
            code=(
                '# @intract.v1 scope:function intent:validate:user forbid:network\n'
                "import requests\n"
                "def validate_user():\n"
                '    return requests.get("https://example.com")\n'
            ),
            language="python",
            filename="auth.py",
        ),
        {},
    )

    assert result.has_errors
    assert result.score == 0.0
    assert result.issues[0].severity == Severity.ERROR
    assert result.issues[0].rule == "intract.contract"


def test_intract_validator_missing_dependency(monkeypatch):
    monkeypatch.delitem(sys.modules, "intract", raising=False)
    monkeypatch.delitem(sys.modules, "intract.integrations", raising=False)
    monkeypatch.delitem(sys.modules, "intract.integrations.vallm", raising=False)

    def _fail_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "intract.integrations.vallm" or name.startswith("intract"):
            raise ImportError("intract missing")
        return orig_import(name, globals, locals, fromlist, level)

    orig_import = __import__
    monkeypatch.setattr("builtins.__import__", _fail_import)

    result = IntractValidator().validate(Proposal(code="pass", language="python"), {})
    assert result.score == 1.0
    assert result.details.get("skipped") is True
    assert result.issues[0].rule == "intract.missing"


def test_pipeline_includes_intract_validator(monkeypatch):
    class DummyIntractValidator:
        tier = 2
        name = "intract"

        def __init__(self, settings=None):
            self.settings = settings

        def validate(self, proposal, context):
            return ValidationResult(validator="intract", score=1.0)

    monkeypatch.setattr("vallm.validators.intract.IntractValidator", DummyIntractValidator)

    settings = VallmSettings(
        enable_syntax=False,
        enable_imports=False,
        enable_complexity=False,
        enable_security=False,
        enable_regression=False,
        enable_semantic=False,
        enable_intract=True,
    )
    proposal = Proposal(code="def add(a: int, b: int) -> int:\n    return a + b", language="python")
    result = validate(proposal, settings)
    assert [item.validator for item in result.results] == ["intract"]
    assert result.verdict == Verdict.PASS


@pytest.mark.integration
def test_intract_validator_with_real_intract():
    pytest.importorskip("intract")

    code = (
        '# @intract.v1 scope:function intent:validate:user priority:1 forbid:network\n'
        "import requests\n"
        "def validate_user():\n"
        '    return requests.get("https://example.com")\n'
    )
    result = IntractValidator().validate(Proposal(code=code, language="python"), {})
    assert result.has_errors
