""".gitignore parsing and pattern matching for file exclusion."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional


class GitignoreParser:
    """Parse .gitignore files and match paths against patterns."""
    
    def __init__(self, gitignore_path: Optional[Path] = None):
        self.patterns: list[tuple[str, bool]] = []  # (pattern, is_negation)
        self.root: Path = gitignore_path.parent if gitignore_path else Path.cwd()
        
        if gitignore_path and gitignore_path.exists():
            self._parse(gitignore_path.read_text())
    
    def _parse(self, content: str) -> None:
        """Parse .gitignore content into patterns."""
        for line in content.splitlines():
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Handle negation
            is_negation = line.startswith("!")
            if is_negation:
                line = line[1:]
            
            # Skip empty after removing !
            if not line:
                continue
            
            self.patterns.append((line, is_negation))
    
    def matches(self, path: Path | str) -> bool:
        """Check if a path matches any gitignore pattern (should be excluded).
        
        Returns True if path should be excluded, False if it should be included.
        """
        path = Path(path)
        
        # Get path relative to gitignore root
        try:
            rel_path = path.relative_to(self.root)
        except ValueError:
            # Path is outside root, use as-is
            rel_path = path
        
        rel_str = str(rel_path).replace(os.sep, "/")
        name = path.name
        
        matched = False
        
        for pattern, is_negation in self.patterns:
            if self._match_pattern(rel_str, name, pattern):
                matched = not is_negation  # negation reverses the match
        
        return matched
    
    def _match_pattern(self, rel_path: str, name: str, pattern: str) -> bool:
        """Match a single pattern against a path."""
        # Handle directory-only patterns (ending with /)
        is_dir_pattern = pattern.endswith("/")
        if is_dir_pattern:
            pattern = pattern[:-1]
        
        # Handle patterns with / (path-specific)
        if "/" in pattern:
            # Pattern contains path separator - match against full relative path
            # Also check if any parent directory matches for directory patterns
            if is_dir_pattern:
                # For dir patterns like "node_modules/", match if path is inside that dir
                parts = rel_path.split("/")
                for i, part in enumerate(parts):
                    partial_path = "/".join(parts[:i+1])
                    if self._fnmatch(partial_path, pattern):
                        return True
                return False
            else:
                return self._fnmatch(rel_path, pattern)
        else:
            # No path separator - match against filename only
            # For dir patterns, also check if path is inside a matching directory
            if is_dir_pattern:
                parts = rel_path.split("/")
                return any(self._fnmatch(part, pattern) for part in parts)
            return self._fnmatch(name, pattern)
    
    def _fnmatch(self, name: str, pattern: str) -> bool:
        """Simple fnmatch implementation for gitignore-style patterns."""
        # Convert gitignore pattern to regex
        regex = self._pattern_to_regex(pattern)
        return bool(re.match(regex, name))
    
    def _pattern_to_regex(self, pattern: str) -> str:
        """Convert a gitignore pattern to a regex pattern."""
        # Escape special regex characters except * and ?
        result = []
        i = 0
        
        while i < len(pattern):
            c = pattern[i]
            
            if c == "*":
                # Check for **
                if i + 1 < len(pattern) and pattern[i + 1] == "*":
                    # ** matches anything including /
                    result.append(".*")
                    i += 2
                else:
                    # * matches anything except /
                    result.append("[^/]*")
                    i += 1
            elif c == "?":
                # ? matches any single character except /
                result.append("[^/]")
                i += 1
            elif c == "[":
                # Character class
                end = pattern.find("]", i + 1)
                if end == -1:
                    result.append(re.escape(c))
                    i += 1
                else:
                    char_class = pattern[i + 1:end]
                    # Handle negation in character class
                    if char_class.startswith("!") or char_class.startswith("^"):
                        char_class = "^" + char_class[1:]
                    result.append(f"[{char_class}]")
                    i = end + 1
            elif c == "/":
                # Match path separator
                result.append("/")
                i += 1
            else:
                # Escape other characters
                result.append(re.escape(c))
                i += 1
        
        return "^" + "".join(result) + "$"


def load_gitignore(path: Path | str = ".") -> GitignoreParser:
    """Load .gitignore from a directory."""
    path = Path(path)
    
    if path.is_file():
        gitignore_path = path
        root = path.parent
    else:
        gitignore_path = path / ".gitignore"
        root = path
    
    parser = GitignoreParser(gitignore_path if gitignore_path.exists() else None)
    parser.root = root  # Ensure root is set correctly
    return parser


def get_default_excludes() -> list[str]:
    """Get default exclude patterns used when no .gitignore exists."""
    return [
        # Version control
        ".git/",
        ".svn/",
        ".hg/",
        ".bzr/",
        
        # Python
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".Python",
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "*.egg-info/",
        ".installed.cfg",
        "*.egg",
        "MANIFEST",
        "venv/",
        "ENV/",
        "env/",
        ".venv/",
        
        # Node
        "node_modules/",
        "npm-debug.log*",
        "yarn-debug.log*",
        "yarn-error.log*",
        ".npm/",
        ".yarn/",
        
        # IDEs
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        "*~",
        ".DS_Store",
        
        # Testing
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        ".tox/",
        ".nox/",
        
        # Documentation
        "site/",
        "docs/_build/",
        
        # Misc
        ".cache/",
        "*.tmp",
        "*.temp",
        ".mypy_cache/",
        ".ruff_cache/",
    ]


def create_default_gitignore_parser() -> GitignoreParser:
    """Create a parser with default exclude patterns."""
    parser = GitignoreParser()
    parser.root = Path.cwd()
    
    for pattern in get_default_excludes():
        parser.patterns.append((pattern, False))
    
    return parser


def should_exclude(
    path: Path,
    gitignore_parser: Optional[GitignoreParser] = None,
    use_defaults: bool = True,
) -> bool:
    """Check if a path should be excluded.
    
    Args:
        path: Path to check
        gitignore_parser: Optional parser from .gitignore file
        use_defaults: Whether to use default excludes when .gitignore doesn't match
    
    Returns:
        True if path should be excluded
    """
    # Check .gitignore first
    if gitignore_parser and gitignore_parser.matches(path):
        return True
    
    # Fall back to defaults
    if use_defaults:
        default_parser = create_default_gitignore_parser()
        return default_parser.matches(path)
    
    return False
