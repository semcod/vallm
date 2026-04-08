"""File discovery helpers for vallm batch processing."""

from __future__ import annotations

from pathlib import Path


def build_file_list(paths: list[Path], recursive: bool) -> list[Path]:
    """Build list of files from input paths."""
    files_to_validate: list[Path] = []

    for path in paths:
        if path.is_file():
            files_to_validate.append(path)
        elif path.is_dir():
            if recursive:
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        files_to_validate.append(file_path)
            else:
                for file_path in path.iterdir():
                    if file_path.is_file():
                        files_to_validate.append(file_path)

    return files_to_validate
