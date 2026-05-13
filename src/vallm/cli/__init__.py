"""CLI package for vallm."""

from __future__ import annotations

import typer

from vallm.cli.batch_processor import BatchProcessor
from vallm.cli.command_handlers import (
    batch_command,
    check_command,
    info_command,
    validate_command,
)

app = typer.Typer(
    name="vallm",
    help="Validate LLM-generated code with a multi-tier pipeline.",
    no_args_is_help=True,
)

# Register commands
app.command(name="validate")(validate_command)
app.command(name="check")(check_command)
app.command(name="batch")(batch_command)
app.command(name="info")(info_command)

# Backward compatibility aliases
batch = batch_command
validate = validate_command
check = check_command
info = info_command

__all__ = [
    "app",
    "BatchProcessor",
    "validate_command",
    "check_command",
    "batch_command",
    "info_command",
    # Backward compatibility
    "validate",
    "check",
    "batch",
    "info",
]
