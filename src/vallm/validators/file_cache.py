"""File-level validation cache using mtime+size fingerprints.

Skips re-validation when a file has not changed since the last run.
Especially effective in pyqual loops where most files stay unchanged
between iterations.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple

from vallm.scoring import PipelineResult


_FileKey = Tuple[str, float, int]  # (absolute_path, mtime, size)


class FileValidationCache:
    """In-memory cache keyed on file path + mtime + size."""

    def __init__(self) -> None:
        self._cache: Dict[_FileKey, PipelineResult] = {}
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _key(file_path: Path) -> Optional[_FileKey]:
        try:
            st = file_path.stat()
            return (str(file_path.resolve()), st.st_mtime, st.st_size)
        except OSError:
            return None

    def get(self, file_path: Path) -> Optional[PipelineResult]:
        key = self._key(file_path)
        if key is None:
            self._misses += 1
            return None
        result = self._cache.get(key)
        if result is not None:
            self._hits += 1
        else:
            self._misses += 1
        return result

    def set(self, file_path: Path, result: PipelineResult) -> None:
        key = self._key(file_path)
        if key is not None:
            self._cache[key] = result

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    @property
    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 2) if total else 0.0,
        }


_global_file_cache: Optional[FileValidationCache] = None


def get_file_cache() -> FileValidationCache:
    global _global_file_cache
    if _global_file_cache is None:
        _global_file_cache = FileValidationCache()
    return _global_file_cache


def clear_file_cache() -> None:
    global _global_file_cache
    if _global_file_cache is not None:
        _global_file_cache.clear()
