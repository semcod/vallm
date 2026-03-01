"""Tests for the import validator."""

from vallm.core.proposal import Proposal
from vallm.validators.imports import ImportValidator


def test_valid_imports():
    code = "import os\nimport json\nfrom pathlib import Path"
    proposal = Proposal(code=code, language="python")
    result = ImportValidator().validate(proposal, {})
    assert result.score == 1.0


def test_missing_import():
    code = "import nonexistent_module_xyz_12345"
    proposal = Proposal(code=code, language="python")
    result = ImportValidator().validate(proposal, {})
    assert result.score < 1.0
    assert any("nonexistent_module_xyz_12345" in i.message for i in result.issues)


def test_no_imports():
    code = "x = 1 + 2"
    proposal = Proposal(code=code, language="python")
    result = ImportValidator().validate(proposal, {})
    assert result.score == 1.0


def test_non_python_skipped():
    code = "const x = require('fs');"
    proposal = Proposal(code=code, language="javascript")
    result = ImportValidator().validate(proposal, {})
    assert result.score == 1.0
    assert result.details.get("skipped") == "non-python"
