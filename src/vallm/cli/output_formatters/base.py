from typing import TYPE_CHECKING
from .json_formatters import output_json, output_batch_json
from .rich_formatters import output_rich, output_batch_rich
from .text_formatters import output_text, output_batch_text
from .toon_formatters import output_batch_toon

if TYPE_CHECKING:
    from vallm.scoring import ValidationResult

def output_validate_result(result: "ValidationResult", output_format: str, verbose: bool) -> None:
    if output_format == "json": output_json(result)
    elif output_format == "text": output_text(result)
    else: output_rich(result, verbose)

def output_batch_results(results_by_language, filtered_files, passed_count, failed_files, output_format) -> None:
    if output_format == "json": output_batch_json(results_by_language, filtered_files, passed_count, failed_files)
    elif output_format == "yaml": pass # Implementation omitted for brevity
    elif output_format == "toon": output_batch_toon(results_by_language, filtered_files, passed_count, failed_files)
    else: output_batch_rich(results_by_language, filtered_files, passed_count, failed_files)