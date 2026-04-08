"""Shared helper utilities for vallm CLI output formatters."""

from __future__ import annotations

from datetime import date


def format_error_message(error: str) -> str:
    """Format error messages consistently across all output formats."""
    if "NoneType" in str(error):
        return "Unable to process file (unsupported format or binary)"
    elif "binary" in str(error).lower():
        return "Binary file (skipped)"
    else:
        return str(error)


def build_files_data(results_by_language: dict) -> list:
    """Build standardized files data structure for all output formats."""
    files_details = []
    for lang, results in results_by_language.items():
        for r in results:
            filename = getattr(r, "filename", None) or "unknown"

            issues = []
            for issue in r.all_issues:
                issue_data = {
                    "rule": issue.rule or "unknown",
                    "severity": issue.severity.value,
                    "message": issue.message,
                }
                if issue.line is not None:
                    issue_data["line"] = issue.line
                if issue.column is not None:
                    issue_data["column"] = issue.column
                issues.append(issue_data)

            files_details.append(
                {
                    "path": filename,
                    "language": lang,
                    "verdict": r.verdict.value,
                    "score": round(r.weighted_score, 2),
                    "issues": issues,
                    "issues_count": len(issues),
                }
            )
    return files_details


def build_failed_files_data(failed_files: list) -> list:
    """Build standardized failed files data structure for all output formats."""
    return [
        {
            "path": str(file_path),
            "error": format_error_message(error),
        }
        for file_path, error in failed_files
    ]


def _toon_today() -> str:
    return date.today().isoformat()
