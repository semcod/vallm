"""Tests for the syntax validator."""

from vallm.core.proposal import Proposal
from vallm.validators.syntax import SyntaxValidator


def test_valid_python():
    proposal = Proposal(code="def foo(): return 1", language="python")
    result = SyntaxValidator().validate(proposal, {})
    assert result.score == 1.0
    assert not result.issues


def test_invalid_python():
    proposal = Proposal(code="def foo(:\n  return", language="python")
    result = SyntaxValidator().validate(proposal, {})
    assert result.score == 0.0
    assert result.has_errors


def test_valid_javascript():
    proposal = Proposal(code="const x = (a, b) => a + b;", language="javascript")
    result = SyntaxValidator().validate(proposal, {})
    assert result.score == 1.0


def test_invalid_javascript():
    proposal = Proposal(code="function foo( { return; }", language="javascript")
    result = SyntaxValidator().validate(proposal, {})
    assert result.score == 0.0


def test_valid_c():
    proposal = Proposal(code="int main() { return 0; }", language="c")
    result = SyntaxValidator().validate(proposal, {})
    assert result.score == 1.0


def test_empty_code():
    proposal = Proposal(code="", language="python")
    result = SyntaxValidator().validate(proposal, {})
    assert result.score == 1.0
