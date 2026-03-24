# System Architecture Analysis

## Overview

- **Project**: vallm
- **Language**: python
- **Files**: 33
- **Lines**: 10012
- **Functions**: 198
- **Classes**: 32
- **Avg CC**: 3.6
- **Critical (CC≥10)**: 9

## Architecture

### mcp/ (1 files, 1L, 0 functions)

- `__init__.py` — 1L, 0 methods, CC↑0

### mcp/server/ (3 files, 694L, 13 functions)

- `_tools_vallm.py` — 508L, 8 methods, CC↑22
- `self_server.py` — 185L, 5 methods, CC↑6
- `__init__.py` — 1L, 0 methods, CC↑0

### root/ (2 files, 49L, 0 functions)

- `mcp_server.py` — 28L, 0 methods, CC↑0
- `project.sh` — 21L, 0 methods, CC↑0

### scripts/ (1 files, 78L, 2 functions)

- `bump_version.py` — 78L, 2 methods, CC↑5

### src/vallm/ (5 files, 334L, 12 functions)

- `scoring.py` — 218L, 8 methods, CC↑7
- `config.py` — 59L, 1 methods, CC↑3
- `hookspecs.py` — 33L, 3 methods, CC↑1
- `__init__.py` — 19L, 0 methods, CC↑0
- `__main__.py` — 5L, 0 methods, CC↑0

### src/vallm/cli/ (4 files, 1125L, 39 functions)

- `batch_processor.py` — 319L, 12 methods, CC↑26
- `output_formatters.py` — 421L, 16 methods, CC↑17
- `command_handlers.py` — 342L, 11 methods, CC↑6
- `__init__.py` — 43L, 0 methods, CC↑0

### src/vallm/core/ (6 files, 778L, 26 functions)

- `gitignore.py` — 272L, 10 methods, CC↑11
- `graph_diff.py` — 104L, 3 methods, CC↑9
- `languages.py` — 227L, 6 methods, CC↑6
- `ast_compare.py` — 135L, 7 methods, CC↑4
- `__init__.py` — 3L, 0 methods, CC↑0
- _1 more files_

### src/vallm/sandbox/ (2 files, 145L, 4 functions)

- `runner.py` — 144L, 4 methods, CC↑4
- `__init__.py` — 1L, 0 methods, CC↑0

### src/vallm/validators/ (10 files, 1628L, 57 functions)

- `complexity.py` — 183L, 4 methods, CC↑12
- `lint.py` — 182L, 6 methods, CC↑9
- `security.py` — 255L, 5 methods, CC↑9
- `regression.py` — 265L, 10 methods, CC↑7
- `logical.py` — 142L, 5 methods, CC↑6
- _5 more files_

### src/vallm/validators/imports/ (11 files, 867L, 45 functions)

- `utils.py` — 150L, 2 methods, CC↑27
- `java_imports.py` — 68L, 5 methods, CC↑7
- `python_imports.py` — 113L, 6 methods, CC↑7
- `c_imports.py` — 88L, 4 methods, CC↑5
- `go_imports.py` — 84L, 5 methods, CC↑5
- _6 more files_

## Key Exports

- **walk** (function, CC=27) ⚠ split
- **BatchProcessor** (class, CC̄=5.6)
  - `_process_files` CC=26 ⚠ split
- **validate_code** (function, CC=22) ⚠ split
- **output_batch_toon** (function, CC=17) ⚠ split
- **ComplexityValidator** (class, CC̄=6.8)
- **GitignoreParser** (class, CC̄=5.7)
- **SecurityValidator** (class, CC̄=5.4)

## Hotspots (High Fan-Out)

- **JavaScriptImportValidator.extract_imports** — fan-out=14: Extract import statements from JavaScript/TypeScript using tree-sitter.
- **GoImportValidator.extract_imports** — fan-out=13: Extract import statements from Go using tree-sitter.
- **RustImportValidator.extract_imports** — fan-out=13: Extract use statements from Rust using tree-sitter.
- **validate_code** — fan-out=12: Full pipeline validation combining multiple validators.

Args:
    code: Source 
- **LintValidator._parse_ruff_text** — fan-out=12: Parse ruff text output as fallback.

Args:
    output: Ruff text output
    
Ret
- **BatchProcessor._process_files** — fan-out=12: Analysis pipeline, 12 stages
- **main** — fan-out=11: Orchestrates 11 calls

## Refactoring Priorities

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Split BatchProcessor._process_files (CC=26 → target CC<10) | high | low |
| 2 | Split walk (CC=27 → target CC<10) | high | low |
| 3 | Split god module mcp/server/_tools_vallm.py (508L, 0 classes) | high | high |
| 4 | Split validate_code (CC=22 → target CC<10) | medium | low |
| 5 | Split output_batch_toon (CC=17 → target CC<10) | medium | low |

## Context for LLM

When suggesting changes:
1. Start from hotspots and high-CC functions
2. Follow refactoring priorities above
3. Maintain public API surface — keep backward compatibility
4. Prefer minimal, incremental changes

