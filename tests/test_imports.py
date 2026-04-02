"""Tests for the import validator."""

import tempfile
import os
from pathlib import Path
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
    assert result.details.get("language") == "javascript"


def test_valid_relative_import():
    """Test that valid relative imports are resolved correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a package structure
        pkg_dir = Path(tmpdir) / "mypackage"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        
        module_a = pkg_dir / "module_a.py"
        module_a.write_text("def foo(): pass")
        
        module_b = pkg_dir / "module_b.py"
        module_b.write_text("from .module_a import foo")
        
        # Test the import
        proposal = Proposal(
            code="from .module_a import foo",
            language="python",
            filename=str(module_b)
        )
        result = ImportValidator().validate(proposal, {})
        assert result.score == 1.0, f"Expected valid relative import, got issues: {result.issues}"


def test_valid_relative_import_parent():
    """Test that valid parent relative imports are resolved correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a package structure
        pkg_dir = Path(tmpdir) / "mypackage"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        
        subpkg_dir = pkg_dir / "subpackage"
        subpkg_dir.mkdir()
        (subpkg_dir / "__init__.py").write_text("")
        
        module_a = pkg_dir / "module_a.py"
        module_a.write_text("def foo(): pass")
        
        module_b = subpkg_dir / "module_b.py"
        module_b.write_text("from ..module_a import foo")
        
        # Test the import
        proposal = Proposal(
            code="from ..module_a import foo",
            language="python",
            filename=str(module_b)
        )
        result = ImportValidator().validate(proposal, {})
        assert result.score == 1.0, f"Expected valid parent relative import, got issues: {result.issues}"


def test_invalid_relative_import():
    """Test that invalid relative imports are detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = Path(tmpdir) / "mypackage"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        
        module_a = pkg_dir / "module_a.py"
        module_a.write_text("from .nonexistent import something")
        
        proposal = Proposal(
            code="from .nonexistent import something",
            language="python",
            filename=str(module_a)
        )
        result = ImportValidator().validate(proposal, {})
        assert result.score < 1.0, "Expected error for nonexistent relative import"
        assert any("nonexistent" in i.message for i in result.issues)
