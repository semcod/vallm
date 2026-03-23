"""Shared save_data function for ollama demo examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def save_data(data: Dict[str, Any], filename: str) -> None:
    """Save data to JSON file.
    
    Args:
        data: Dictionary to save
        filename: Output filename
    """
    output_path = Path(filename)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {output_path}")
