"""Tests for the security validator."""

from vallm.core.proposal import Proposal
from vallm.validators.security import SecurityValidator


def test_safe_code():
    code = "def add(a, b):\n    return a + b"
    proposal = Proposal(code=code, language="python")
    result = SecurityValidator().validate(proposal, {})
    assert result.score == 1.0
    assert not result.issues


def test_eval_detected():
    code = "result = eval(user_input)"
    proposal = Proposal(code=code, language="python")
    result = SecurityValidator().validate(proposal, {})
    assert result.score < 1.0
    assert any("eval" in i.message.lower() for i in result.issues)


def test_exec_detected():
    code = "exec('print(1)')"
    proposal = Proposal(code=code, language="python")
    result = SecurityValidator().validate(proposal, {})
    assert result.score < 1.0


def test_hardcoded_secret():
    code = 'api_key = "sk-secret123"'
    proposal = Proposal(code=code, language="python")
    result = SecurityValidator().validate(proposal, {})
    assert any("secret" in i.message.lower() or "key" in i.message.lower() for i in result.issues)
