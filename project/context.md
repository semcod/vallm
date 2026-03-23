# System Architecture Analysis

## Overview

- **Project**: vallm
- **Language**: python
- **Files**: 31
- **Lines**: 7605
- **Functions**: 185
- **Classes**: 32
- **Avg CC**: 3.5
- **Critical (CC≥10)**: 9

## Architecture

### root/ (1 files, 18L, 0 functions)

- `project.sh` — 18L, 0 methods, CC↑0

### scripts/ (1 files, 78L, 2 functions)

- `bump_version.py` — 78L, 2 methods, CC↑5

### src/vallm/ (5 files, 327L, 12 functions)

- `scoring.py` — 212L, 8 methods, CC↑6
- `config.py` — 58L, 1 methods, CC↑3
- `hookspecs.py` — 33L, 3 methods, CC↑1
- `__init__.py` — 19L, 0 methods, CC↑0
- `__main__.py` — 5L, 0 methods, CC↑0

### src/vallm/cli/ (5 files, 1243L, 49 functions)

- `optimized_batch_processor.py` — 346L, 13 methods, CC↑19
- `batch_processor.py` — 262L, 12 methods, CC↑18
- `output_formatters.py` — 306L, 13 methods, CC↑7
- `command_handlers.py` — 297L, 11 methods, CC↑4
- `__init__.py` — 32L, 0 methods, CC↑0

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

### src/vallm/validators/ (9 files, 1361L, 47 functions)

- `complexity.py` — 183L, 4 methods, CC↑12
- `lint.py` — 182L, 6 methods, CC↑9
- `security.py` — 253L, 5 methods, CC↑9
- `logical.py` — 142L, 5 methods, CC↑6
- `semantic_cache.py` — 187L, 8 methods, CC↑5
- _4 more files_

### src/vallm/validators/imports/ (11 files, 867L, 45 functions)

- `utils.py` — 150L, 2 methods, CC↑27
- `java_imports.py` — 68L, 5 methods, CC↑7
- `python_imports.py` — 113L, 6 methods, CC↑7
- `c_imports.py` — 88L, 4 methods, CC↑5
- `go_imports.py` — 84L, 5 methods, CC↑5
- _6 more files_

## Key Exports

- **walk** (function, CC=27) ⚠ split
- **OptimizedBatchProcessor** (class, CC̄=6.5)
  - `_process_files_sequential` CC=15 ⚠ split
  - `_process_files_parallel` CC=19 ⚠ split
- **BatchProcessor** (class, CC̄=4.8)
  - `_process_files` CC=18 ⚠ split
- **ComplexityValidator** (class, CC̄=6.8)
- **GitignoreParser** (class, CC̄=5.7)
- **SecurityValidator** (class, CC̄=5.4)

## Hotspots (High Fan-Out)

- **OptimizedBatchProcessor._process_files_parallel** — fan-out=16: Analysis pipeline, 16 stages
- **JavaScriptImportValidator.extract_imports** — fan-out=14: Extract import statements from JavaScript/TypeScript using tree-sitter.
- **GoImportValidator.extract_imports** — fan-out=13: Extract import statements from Go using tree-sitter.
- **RustImportValidator.extract_imports** — fan-out=13: Extract use statements from Rust using tree-sitter.
- **LintValidator._parse_ruff_text** — fan-out=12: Parse ruff text output as fallback.

Args:
    output: Ruff text output
    
Ret
- **main** — fan-out=11: Orchestrates 11 calls
- **SemanticValidator._parse_response** — fan-out=11: Parse LLM JSON response into a ValidationResult.

## Refactoring Priorities

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Split walk (CC=27 → target CC<10) | high | low |
| 2 | Split OptimizedBatchProcessor._process_files_sequential (CC=15 → target CC<10) | medium | low |
| 3 | Split OptimizedBatchProcessor._process_files_parallel (CC=19 → target CC<10) | medium | low |
| 4 | Split BatchProcessor._process_files (CC=18 → target CC<10) | medium | low |
| 5 | Reduce OptimizedBatchProcessor._process_files_parallel fan-out (currently 16) | medium | medium |

## Context for LLM

When suggesting changes:
1. Start from hotspots and high-CC functions
2. Follow refactoring priorities above
3. Maintain public API surface — keep backward compatibility
4. Prefer minimal, incremental changes

