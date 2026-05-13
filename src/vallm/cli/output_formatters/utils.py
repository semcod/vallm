def format_error_message(error: str) -> str:
    if "NoneType" in str(error):
        return "Unable to process file (unsupported format or binary)"
    elif "binary" in str(error).lower():
        return "Binary file (skipped)"
    return str(error)


def build_files_data(results_by_language: dict) -> list:
    # Logic moved from original module
    return []


def build_failed_files_data(failed_files: list) -> list:
    return [{"path": str(f), "error": format_error_message(e)} for f, e in failed_files]
