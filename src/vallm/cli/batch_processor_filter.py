from __future__ import annotations
from pathlib import Path
from typing import Optional
from vallm.cli.batch_constants import _DEFAULT_EXCLUDE_PATTERNS
from vallm.cli.batch_processor_patterns import TOON_EXTENSIONS, _CompiledPatterns, _compile_patterns


def parse_filter_patterns(include: Optional[str], exclude: Optional[str]) -> dict:
    raw_exclude = list(_DEFAULT_EXCLUDE_PATTERNS)
    if exclude:
        raw_exclude.extend(exclude.split(","))
    raw_include = include.split(",") if include else []
    return {"exclude": _compile_patterns(raw_exclude), "include": _compile_patterns(raw_include)}


def should_exclude_file(file_path: Path, compiled: _CompiledPatterns) -> bool:
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
    if compiled.is_empty:
        return True
    file_name = file_path.name
    if file_name in compiled.exact:
        return True
    return bool(compiled.regex and compiled.regex.search(file_name))
