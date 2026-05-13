"""Shared utilities for ollama simple demo examples."""

from __future__ import annotations

from .calculate_total import calculate_total
from .load_config import load_config
from .main import run_demo_main
from .process_user_input import process_user_input
from .save_data import save_data

__all__ = [
    "calculate_total",
    "load_config",
    "run_demo_main",
    "process_user_input",
    "save_data",
]
