"""Validation execution helpers for vallm batch processing."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from vallm.config import VallmSettings
from vallm.core.languages import detect_language
from vallm.core.proposal import Proposal
from vallm.scoring import validate
from vallm.validators.file_cache import get_file_cache

_MAX_WORKERS = min(__import__("os").cpu_count() or 1, 8)


def validate_single_file(file_path: Path, settings: VallmSettings):
    """Validate a single file (top-level for thread-pool compatibility)."""
    lang_obj = detect_language(file_path)
    if lang_obj is None:
        return file_path, None, None, "Unsupported file type"

    cache = get_file_cache()
    cached = cache.get(file_path)
    if cached is not None:
        return file_path, lang_obj, cached, None

    try:
        code = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path, None, None, "Unable to read file (binary?)"

    proposal = Proposal(
        code=code,
        language=lang_obj.tree_sitter_id,
        filename=str(file_path),
    )
    result = validate(proposal, settings)
    cache.set(file_path, result)
    return file_path, lang_obj, result, None


def process_files(
    files: list[Path],
    settings: VallmSettings,
    output_format: str,
    fail_fast: bool,
    verbose: bool,
    show_issues: bool,
):
    """Validate files concurrently and aggregate results."""
    results_by_language: dict = {}
    failed_files: list = []
    passed_count = 0
    processed_count = 0

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {executor.submit(validate_single_file, file_path, settings): file_path for file_path in files}
        for future in as_completed(futures):
            file_path, lang_obj, result, error = future.result()
            processed_count += 1

            if error is not None:
                failed_files.append((file_path, error))
                if fail_fast:
                    break
                continue

            language_name = getattr(lang_obj, "name", "unknown")
            results_by_language.setdefault(language_name, []).append(result)
            if getattr(result, "passed", False):
                passed_count += 1
            else:
                failed_files.append((file_path, result))
                if fail_fast:
                    break

    return results_by_language, failed_files, passed_count, processed_count
