"""File filtering utilities for batch processing."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from vallm.cli.batch_constants import _DEFAULT_EXCLUDE_PATTERNS
from vallm.cli.batch_processor_patterns import TOON_EXTENSIONS, _CompiledPatterns, _compile_patterns
from vallm.core.gitignore import load_gitignore


def parse_filter_patterns(include: Optional[str], exclude: Optional[str]) -> dict:
    """Parse include and exclude patterns into compiled matchers."""
    raw_exclude: list[str] = list(_DEFAULT_EXCLUDE_PATTERNS)
    if exclude:
        raw_exclude.extend(exclude.split(","))

    raw_include: list[str] = []
    if include:
        raw_include = include.split(",")

    return {
        "exclude": _compile_patterns(raw_exclude),
        "include": _compile_patterns(raw_include),
    }


def should_exclude_file(file_path: Path, compiled: _CompiledPatterns) -> bool:
    """Check if file should be excluded based on pre-compiled patterns."""
    file_name = file_path.name
    file_str_lower = str(file_path).lower()

    if any(file_str_lower.endswith(ext) for ext in TOON_EXTENSIONS):
        return True

    if file_name in compiled.exact or any(part in compiled.exact for part in file_path.parts):
        return True

    if compiled.regex and (
        compiled.regex.search(file_name)
        or any(compiled.regex.search(part) for part in file_path.parts)
    ):
        return True

    return False


def matches_include_pattern(file_path: Path, compiled: _CompiledPatterns) -> bool:
    """Check if file matches pre-compiled include patterns."""
    if compiled.is_empty:
        return True

    file_name = file_path.name
    if file_name in compiled.exact:
        return True

    if compiled.regex and compiled.regex.search(file_name):
        return True

    return False


def load_vallmignore():
    """Load .vallmignore from the current working directory if it exists."""
    vallmignore_path = Path.cwd() / ".vallmignore"
    if not vallmignore_path.exists():
        return None
    parser = load_gitignore(vallmignore_path)
    return parser


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
    excluded_by_vallmignore = 0

    patterns = parse_filter_patterns(include, exclude)
    vallmignore_parser = load_vallmignore()

    for f in files:
        if use_gitignore and gitignore_parser and gitignore_parser.matches(f):
            excluded_by_gitignore += 1
            continue

        if vallmignore_parser and vallmignore_parser.matches(f):
            excluded_by_vallmignore += 1
            continue

        if should_exclude_file(f, patterns["exclude"]):
            continue

        if matches_include_pattern(f, patterns["include"]):
            filtered_files.append(f)

    if excluded_by_gitignore > 0:
        console.print(f"[dim]Excluded {excluded_by_gitignore} files by .gitignore[/dim]")
    if excluded_by_vallmignore > 0:
        console.print(f"[dim]Excluded {excluded_by_vallmignore} files by .vallmignore[/dim]")

    return filtered_files
