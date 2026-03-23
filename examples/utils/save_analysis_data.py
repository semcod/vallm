"""Shared utility for saving analysis data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def save_analysis_data(example_name: str, result_data: Dict[str, Any]) -> None:
    """Save analysis data to JSON file.
    
    Args:
        example_name: Name of the example (used for filename)
        result_data: Dictionary containing validation results
    """
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    summary_file = output_dir / f"{example_name}_summary.json"
    
    with open(summary_file, "w") as f:
        json.dump(result_data, f, indent=2, default=str)
    
    print(f"Analysis data saved to {summary_file}")
