"""Pattern compilation and file filtering helpers for vallm batch processing."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

TOON_EXTENSIONS = {".toon.yaml", ".toon"}


class _CompiledPatterns:
    """Pre-compiled pattern set: exact names in a frozenset, globs in one regex."""

    __slots__ = ("exact", "regex", "is_empty")

    def __init__(self, exact: frozenset[str], regex, is_empty: bool):
        self.exact = exact
        self.regex = regex
        self.is_empty = is_empty


def _compile_patterns(raw: list[str]) -> _CompiledPatterns:
    """Split raw glob strings into an exact-match set and a combined regex."""
    import fnmatch
    import re

    if not raw:
        return _CompiledPatterns(frozenset(), None, True)

    exact: set[str] = set()
    regex_parts: list[str] = []

    for pat in dict.fromkeys(raw):
        if any(c in pat for c in ("*", "?", "[", "]")):
            regex_parts.append(fnmatch.translate(pat))
        else:
            exact.add(pat)

    compiled_re = re.compile("|".join(regex_parts)) if regex_parts else None
    return _CompiledPatterns(frozenset(exact), compiled_re, False)


_DEFAULT_EXCLUDES = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "__pycache__",
    ".pytest_cache",
    "*.egg-info",
    "build",
    "dist",
    ".tox",
    ".coverage",
    "htmlcov",
    ".git",
    ".gitignore",
    ".gitmodules",
    ".github",
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "venv",
    "env",
    ".venv",
    "ENV",
    "virtualenv",
    "publish-env",
    "node_modules",
    "npm-debug.log*",
    "yarn-debug.log*",
    "yarn-error.log*",
    "build",
    "dist",
    "target",
    "bin",
    "out",
    ".cache",
    "cache",
    "*.cache",
    "tmp",
    "temp",
    "*.tmp",
    "*.temp",
    "*.log",
    "logs",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".coverage",
    "_build",
    "site",
    ".doctrees",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
]


def parse_filter_patterns(include: Optional[str], exclude: Optional[str]) -> dict:
    """Parse include and exclude patterns into compiled matchers."""
    raw_exclude: list[str] = []
    if exclude:
        raw_exclude = exclude.split(",")

    raw_exclude.extend(_DEFAULT_EXCLUDES)
    include_raw = include.split(",") if include else []

    return {
        "include": _compile_patterns(include_raw),
        "exclude": _compile_patterns(raw_exclude),
    }


def matches_pattern(path: Path, compiled: _CompiledPatterns) -> bool:
    """Check whether a path matches compiled patterns."""
    if compiled.is_empty:
        return True

    name = path.name
    if name in compiled.exact:
        return True
    if compiled.regex is not None and compiled.regex.match(name):
        return True
    return False


def should_exclude_file(path: Path, exclude_patterns: _CompiledPatterns) -> bool:
    """Return True if the file should be excluded."""
    return not matches_pattern(path, exclude_patterns)


def matches_include_pattern(path: Path, include_patterns: _CompiledPatterns) -> bool:
    """Return True if the file matches include patterns."""
    return matches_pattern(path, include_patterns)


def filter_files(
    files: list[Path],
    include: Optional[str],
    exclude: Optional[str],
    gitignore_parser,
    use_gitignore: bool,
    console,
) -> list[Path]:
    """Filter files based on patterns and gitignore."""
    filtered_files: list[Path] = []
    excluded_by_gitignore = 0

    patterns = parse_filter_patterns(include, exclude)

    for f in files:
        if use_gitignore and gitignore_parser and gitignore_parser.matches(f):
            excluded_by_gitignore += 1
            continue

        if should_exclude_file(f, patterns["exclude"]):
            continue

        if matches_include_pattern(f, patterns["include"]):
            filtered_files.append(f)

    if excluded_by_gitignore > 0:
        console.print(f"[dim]Excluded {excluded_by_gitignore} files by .gitignore[/dim]")

    return filtered_files
