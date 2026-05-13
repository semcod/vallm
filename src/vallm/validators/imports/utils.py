"""Shared utilities for import validators."""

import os
from pathlib import Path
from typing import Callable, Iterator, Optional

_TEST_DIR_NAMES = frozenset(
    ("tests", "test", "__pycache__", "venv", ".venv", "node_modules", "vendor")
)
_SKIP_ROOT_NAMES = frozenset(("tests", "test", "__pycache__", "venv", ".venv", "node_modules"))


def _is_gitignored(
    path: Path,
    project_root: Optional[Path],
    gitignore_matcher: Optional[Callable[[Path], bool]],
) -> bool:
    """Return True if path matches gitignore rules."""
    if not gitignore_matcher or not project_root:
        return False
    try:
        return gitignore_matcher(path.relative_to(project_root))
    except ValueError:
        return False


def _should_skip_dir(name: str, skip_tests: bool, skip_hidden: bool) -> bool:
    """Return True if a directory should be skipped entirely."""
    if skip_hidden and name.startswith("."):
        return True
    if skip_tests and name in _TEST_DIR_NAMES:
        return True
    return False


def _should_skip_entry(
    path: Path,
    name: str,
    project_root: Optional[Path],
    gitignore_matcher: Optional[Callable[[Path], bool]],
    skip_tests: bool,
    skip_hidden: bool,
) -> bool:
    """Check if a directory entry should be skipped."""
    if _should_skip_dir(name, skip_tests, skip_hidden):
        return True
    if _is_gitignored(path, project_root, gitignore_matcher):
        return True
    return False


def walk(
    root: Path,
    project_root: Optional[Path] = None,
    gitignore_matcher: Optional[Callable[[Path], bool]] = None,
    skip_tests: bool = True,
    skip_hidden: bool = True,
    max_depth: Optional[int] = None,
    current_depth: int = 0,
) -> Iterator[Path]:
    """Walk directory tree yielding Python files.

    Args:
        root: Root directory to start walking
        project_root: Project root for relative path calculations
        gitignore_matcher: Optional function to check if path matches gitignore
        skip_tests: Whether to skip test directories
        skip_hidden: Whether to skip hidden files/directories
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth (internal use)

    Yields:
        Path objects for each Python file
    """
    if max_depth is not None and current_depth > max_depth:
        return

    if _should_skip_entry(
        root, root.name, project_root, gitignore_matcher, skip_tests, skip_hidden
    ):
        return

    for entry in os.scandir(root):
        entry_path = Path(entry.path)

        if entry.is_dir(follow_symlinks=False):
            if _should_skip_entry(
                entry_path, entry.name, project_root, gitignore_matcher, skip_tests, skip_hidden
            ):
                continue
            yield from walk(
                entry_path,
                project_root,
                gitignore_matcher,
                skip_tests,
                skip_hidden,
                max_depth,
                current_depth + 1,
            )
        elif entry.is_file(follow_symlinks=False):
            if not entry.name.endswith(".py"):
                continue
            if _is_gitignored(entry_path, project_root, gitignore_matcher):
                continue
            yield entry_path


def validate_import_path(
    import_path: str,
    source_file: Path,
    project_root: Path,
    known_modules: set[str],
    stdlib_modules: set[str],
) -> tuple[bool, Optional[str]]:
    """Validate if an import path is resolvable.

    Args:
        import_path: The import path to validate
        source_file: Source file containing the import
        project_root: Project root directory
        known_modules: Set of known third-party module names
        stdlib_modules: Set of standard library module names

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Handle relative imports
    if import_path.startswith("."):
        parts = import_path.split(".")
        dots = len([p for p in parts if p == ""])
        base_path = source_file.parent

        # Go up directories for each dot
        for _ in range(dots - 1):
            base_path = base_path.parent

        # Try to resolve the module
        module_name = parts[-1] if parts[-1] else None
        if module_name:
            target = base_path / f"{module_name}.py"
            if target.exists():
                return True, None

        # Check if it's a package
        if module_name:
            pkg_init = base_path / module_name / "__init__.py"
            if pkg_init.exists():
                return True, None

        return False, f"Cannot resolve relative import: {import_path}"

    # Handle absolute imports
    module_name = import_path.split(".")[0]

    # Check standard library
    if module_name in stdlib_modules:
        return True, None

    # Check known third-party modules
    if module_name in known_modules:
        return True, None

    # Try to resolve as local module
    local_module = project_root / f"{module_name}.py"
    if local_module.exists():
        return True, None

    local_pkg = project_root / module_name / "__init__.py"
    if local_pkg.exists():
        return True, None

    return False, f"Cannot resolve import: {import_path}"
