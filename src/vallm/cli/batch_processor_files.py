"""File discovery helpers for vallm batch processing."""

from __future__ import annotations

import os
from pathlib import Path

from vallm.cli.batch_constants import _DEFAULT_EXCLUDE_PATTERNS
from vallm.cli.batch_processor_filter import should_exclude_file
from vallm.cli.batch_processor_patterns import _compile_patterns

_DEFAULT_EXCLUDE_COMPILED = _compile_patterns(_DEFAULT_EXCLUDE_PATTERNS)


def build_file_list(paths: list[Path], recursive: bool) -> list[Path]:
    """Build list of files from input paths.

    Recursive walks prune directories matching the default exclude
    patterns (venv, node_modules, ...) before descending into them,
    instead of collecting every file with rglob("*") and filtering
    afterward, which fully walks (and stats) a populated virtualenv
    before discarding it.
    """
    files_to_validate: list[Path] = []

    for path in paths:
        if path.is_file():
            files_to_validate.append(path)
        elif path.is_dir():
            if recursive:
                for dirpath, dirnames, filenames in os.walk(path, topdown=True):
                    current_dir = Path(dirpath)
                    dirnames[:] = [
                        d
                        for d in dirnames
                        if not should_exclude_file(current_dir / d, _DEFAULT_EXCLUDE_COMPILED)
                    ]
                    for filename in filenames:
                        files_to_validate.append(current_dir / filename)
            else:
                for file_path in path.iterdir():
                    if file_path.is_file():
                        files_to_validate.append(file_path)

    return files_to_validate
