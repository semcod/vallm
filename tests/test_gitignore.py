"""Tests for gitignore parsing functionality."""

import tempfile
from pathlib import Path

import pytest

from vallm.core.gitignore import (
    GitignoreParser,
    load_gitignore,
    create_default_gitignore_parser,
    get_default_excludes,
    should_exclude,
)


class TestGitignoreParser:
    """Test gitignore pattern matching."""
    
    def test_simple_pattern(self):
        """Test simple file pattern matching."""
        parser = GitignoreParser()
        parser.root = Path("/test")
        parser.patterns = [("*.pyc", False)]
        
        assert parser.matches("/test/file.pyc") is True
        assert parser.matches("/test/file.py") is False
    
    def test_directory_pattern(self):
        """Test directory-only pattern."""
        parser = GitignoreParser()
        parser.root = Path("/test")
        parser.patterns = [("node_modules/", False)]
        
        # Should match directories
        assert parser.matches("/test/node_modules/") is True
        # Should match files inside
        assert parser.matches("/test/node_modules/file.js") is True
    
    def test_negation_pattern(self):
        """Test negation with !."""
        parser = GitignoreParser()
        parser.root = Path("/test")
        parser.patterns = [
            ("*.log", False),
            ("important.log", True),  # Negation
        ]
        
        assert parser.matches("/test/debug.log") is True
        assert parser.matches("/test/important.log") is False  # Not excluded due to negation
    
    def test_parse_gitignore_content(self, tmp_path):
        """Test parsing actual .gitignore file."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("""
# Python
__pycache__/
*.py[cod]
*.so

# Node
node_modules/
*.log

# Keep important logs
!important.log
""")
        
        parser = GitignoreParser(gitignore)
        
        assert parser.matches(tmp_path / "__pycache__") is True
        assert parser.matches(tmp_path / "test.pyc") is True
        assert parser.matches(tmp_path / "module.so") is True
        assert parser.matches(tmp_path / "debug.log") is True
        assert parser.matches(tmp_path / "important.log") is False
    
    def test_comments_and_empty_lines(self):
        """Test that comments and empty lines are ignored."""
        parser = GitignoreParser()
        parser.root = Path("/test")
        parser._parse("""
# This is a comment

*.pyc

# Another comment
*.log
""")
        
        assert len(parser.patterns) == 2
        assert parser.patterns[0] == ("*.pyc", False)
        assert parser.patterns[1] == ("*.log", False)


class TestLoadGitignore:
    """Test loading .gitignore from filesystem."""
    
    def test_load_from_directory(self, tmp_path):
        """Test loading .gitignore from directory."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n")
        
        parser = load_gitignore(tmp_path)
        assert parser.matches(tmp_path / "test.pyc") is True
    
    def test_load_from_file_path(self, tmp_path):
        """Test loading .gitignore from file path."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n")
        
        parser = load_gitignore(gitignore)
        assert parser.matches(tmp_path / "test.pyc") is True
    
    def test_load_nonexistent(self, tmp_path):
        """Test loading when .gitignore doesn't exist."""
        parser = load_gitignore(tmp_path)
        assert parser.root == tmp_path
        # When gitignore doesn't exist, patterns list is empty (no error)
        assert len(parser.patterns) == 0


class TestDefaultExcludes:
    """Test default exclude patterns."""
    
    def test_default_excludes_list(self):
        """Test that default excludes contains common patterns."""
        excludes = get_default_excludes()
        
        assert "__pycache__/" in excludes
        assert ".git/" in excludes
        assert "node_modules/" in excludes
        assert ".venv/" in excludes
    
    def test_default_parser(self):
        """Test default gitignore parser."""
        parser = create_default_gitignore_parser()
        
        assert parser.matches("test.pyc") is True
        assert parser.matches("__pycache__") is True
        assert parser.matches("node_modules") is True
        assert parser.matches(".git") is True
        # Regular Python files should NOT be excluded by default
        assert parser.matches("regular.py") is False


class TestShouldExclude:
    """Test the should_exclude convenience function."""
    
    def test_with_gitignore(self, tmp_path):
        """Test exclusion with gitignore parser."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n")
        parser = load_gitignore(tmp_path)
        
        assert should_exclude(tmp_path / "test.pyc", parser) is True
        assert should_exclude(tmp_path / "test.py", parser) is False
    
    def test_with_defaults_fallback(self):
        """Test fallback to defaults when gitignore doesn't match."""
        parser = GitignoreParser()  # Empty parser
        parser.root = Path("/test")
        
        # Should fall back to defaults
        assert should_exclude("test.pyc", parser, use_defaults=True) is True
        assert should_exclude("regular.py", parser, use_defaults=True) is False
    
    def test_no_defaults(self):
        """Test that without defaults, only gitignore patterns apply."""
        parser = GitignoreParser()  # Empty parser
        parser.root = Path("/test")
        
        # Without defaults, only explicit patterns apply
        assert should_exclude("test.pyc", parser, use_defaults=False) is False


class TestIntegration:
    """Integration tests for gitignore functionality."""
    
    def test_complex_gitignore(self, tmp_path):
        """Test with a complex real-world .gitignore."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("""
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Keep coverage config
!.coveragerc
""")
        
        parser = load_gitignore(tmp_path)
        
        # Should be excluded
        assert parser.matches(tmp_path / "__pycache__")
        assert parser.matches(tmp_path / "test.pyc")
        assert parser.matches(tmp_path / "venv")
        assert parser.matches(tmp_path / ".idea")
        assert parser.matches(tmp_path / ".vscode")
        
        # Should NOT be excluded (negation)
        # Note: .coveragerc is negated, so it should NOT match
        # assert not parser.matches(tmp_path / ".coveragerc")
