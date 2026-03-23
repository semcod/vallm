"""Logging utilities for vallm examples and demos."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"
    DIM = "\033[2m"


def log_section(title: str) -> None:
    """Print a section header.
    
    Args:
        title: Section title
    """
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA} {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*80}{Colors.END}\n")
    logger.info(f"SECTION: {title}")


def log_step(step: int, description: str) -> None:
    """Print a step indicator.
    
    Args:
        step: Step number
        description: Step description
    """
    print(f"\n{Colors.CYAN}Step {step}: {description}{Colors.END}")
    logger.info(f"STEP {step}: {description}")


def log_code(label: str, code: str, max_lines: int = 30) -> None:
    """Log code with label and truncation.
    
    Args:
        label: Code label/description
        code: Code string to display
        max_lines: Maximum lines to show before truncating
    """
    lines = code.split('\n')
    if len(lines) > max_lines:
        show_lines = lines[:max_lines//2] + ['...'] + lines[-max_lines//2:]
        display = '\n'.join(show_lines)
    else:
        display = code
    
    print(f"\n{Colors.BOLD}{label}:{Colors.END}")
    print(f"{Colors.DIM}{display}{Colors.END}")
    print()
    logger.info(f"CODE [{label}]: {len(lines)} lines")


def log_result(status: str, message: str) -> None:
    """Log a result with appropriate color.
    
    Args:
        status: Status type ('success', 'warning', 'error', 'info')
        message: Message to display
    """
    colors = {
        'success': Colors.GREEN,
        'warning': Colors.YELLOW,
        'error': Colors.RED,
        'info': Colors.CYAN,
    }
    icon = {
        'success': '✓',
        'warning': '⚠',
        'error': '✗',
        'info': 'ℹ',
    }
    color = colors.get(status, Colors.END)
    ic = icon.get(status, '?')
    
    print(f"{color}{ic} {message}{Colors.END}")
    logger.info(f"RESULT [{status}]: {message}")
