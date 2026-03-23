"""Shared load_config function for ollama demo examples."""

from __future__ import annotations

from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Load configuration with default values.
    
    Returns:
        Configuration dictionary
    """
    return {
        'app_name': 'Demo App',
        'version': '1.0.0',
        'debug': False,
        'max_items': 100
    }
