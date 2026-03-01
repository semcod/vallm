"""Tests for the complexity validator."""

from vallm.config import VallmSettings
from vallm.core.proposal import Proposal
from vallm.validators.complexity import ComplexityValidator


def test_simple_code():
    code = "def add(a, b):\n    return a + b"
    proposal = Proposal(code=code, language="python")
    result = ComplexityValidator().validate(proposal, {})
    assert result.score == 1.0


def test_complex_code():
    code = """
def complex(a, b, c, d, e, f, g, h):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            if g:
                                if h:
                                    return 1
                                return 2
                            return 3
                        return 4
                    return 5
                return 6
            return 7
        return 8
    return 9
"""
    settings = VallmSettings(max_cyclomatic_complexity=5)
    proposal = Proposal(code=code, language="python")
    result = ComplexityValidator(settings).validate(proposal, {})
    assert result.score < 1.0
    assert len(result.issues) > 0


def test_javascript_lizard():
    code = "function add(a, b) { return a + b; }"
    proposal = Proposal(code=code, language="javascript")
    result = ComplexityValidator().validate(proposal, {})
    assert result.score == 1.0
