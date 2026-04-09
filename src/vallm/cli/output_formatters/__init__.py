"""Output formatting functions for vallm CLI."""

from __future__ import annotations

from datetime import date

from . import batch as _batch
from .shared import build_failed_files_data, build_files_data, format_error_message
from .single import output_json, output_rich, output_text


TOON_UNSUPPORTED_ORDER = _batch.TOON_UNSUPPORTED_ORDER
build_results_table = _batch.build_results_table
output_batch_json = _batch.output_batch_json
output_batch_rich = _batch.output_batch_rich
output_batch_text = _batch.output_batch_text
output_batch_toon = _batch.output_batch_toon
output_batch_yaml = _batch.output_batch_yaml
print_summary_header = _batch.print_summary_header


def _toon_today() -> str:
    return date.today().isoformat()


_batch._toon_today = _toon_today


def output_validate_result(result, output_format: str, verbose: bool) -> None:
    """Output validation result in the specified format."""
    if output_format == "json":
        output_json(result)
    elif output_format == "text":
        output_text(result)
    else:
        output_rich(result, verbose)


def output_batch_results(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
    output_format: str,
) -> None:
    """Output batch validation results in the specified format."""
    if output_format == "json":
        output_batch_json(results_by_language, filtered_files, passed_count, failed_files)
    elif output_format == "yaml":
        output_batch_yaml(results_by_language, filtered_files, passed_count, failed_files)
    elif output_format == "toon":
        output_batch_toon(results_by_language, filtered_files, passed_count, failed_files)
    else:
        output_batch_rich(results_by_language, filtered_files, passed_count, failed_files)


output_batch_empty = _batch.output_batch_empty


__all__ = [
    "date",
    "TOON_UNSUPPORTED_ORDER",
    "build_files_data",
    "build_failed_files_data",
    "build_results_table",
    "format_error_message",
    "output_validate_result",
    "output_batch_results",
    "output_batch_empty",
    "output_json",
    "output_batch_json",
    "output_rich",
    "output_batch_rich",
    "output_text",
    "output_batch_text",
    "output_batch_toon",
    "output_batch_yaml",
    "print_summary_header",
]