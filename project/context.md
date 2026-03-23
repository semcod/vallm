# System Architecture Analysis

## Overview

- **Project**: vallm
- **Language**: python
- **Files**: 16
- **Lines**: 6522
- **Functions**: 114
- **Classes**: 19
- **Avg CC**: 4.6
- **Critical (CC≥10)**: 16

## Architecture

### root/ (1 files, 16L, 0 functions)

- `project.sh` — 16L, 0 methods, CC↑0

### scripts/ (1 files, 78L, 2 functions)

- `bump_version.py` — 78L, 2 methods, CC↑5

### src/vallm/ (6 files, 1221L, 39 functions)

- `cli.py` — 895L, 27 methods, CC↑18
- `scoring.py` — 211L, 8 methods, CC↑6
- `config.py` — 58L, 1 methods, CC↑3
- `hookspecs.py` — 33L, 3 methods, CC↑1
- `__init__.py` — 19L, 0 methods, CC↑0
- _1 more files_

### src/vallm/core/ (6 files, 753L, 26 functions)

- `gitignore.py` — 272L, 10 methods, CC↑11
- `graph_diff.py` — 86L, 3 methods, CC↑6
- `languages.py` — 220L, 6 methods, CC↑6
- `ast_compare.py` — 135L, 7 methods, CC↑4
- `__init__.py` — 3L, 0 methods, CC↑0
- _1 more files_

### src/vallm/sandbox/ (2 files, 145L, 4 functions)

- `runner.py` — 144L, 4 methods, CC↑4
- `__init__.py` — 1L, 0 methods, CC↑0

### src/vallm/validators/ (7 files, 847L, 43 functions)

- `complexity.py` — 183L, 4 methods, CC↑12
- `semantic.py` — 282L, 8 methods, CC↑12
- `imports.py` — 11L, 22 methods, CC↑10
- `security.py` — 253L, 5 methods, CC↑9
- `syntax.py` — 96L, 3 methods, CC↑4
- _2 more files_

## Key Exports

- **validate** (function, CC=18) ⚠ split
- **ComplexityValidator** (class, CC̄=6.8)
- **GitignoreParser** (class, CC̄=5.7)
- **SecurityValidator** (class, CC̄=5.4)

## Hotspots (High Fan-Out)

- **validate** — fan-out=21: Validate a code proposal through the vallm pipeline.
- **SemanticValidator._parse_response** — fan-out=17: Parse LLM JSON response into a ValidationResult.
- **check** — fan-out=13: Quick syntax check only (tier 1).
- **batch** — fan-out=12: Validate multiple files with auto-detected languages.
- **main** — fan-out=11: Orchestrates 11 calls
- **SandboxRunner._run_docker** — fan-out=11: Run code in a Docker container (requires docker package).
- **SecurityValidator._try_bandit** — fan-out=10: Try to run bandit if installed.

## Refactoring Priorities

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Split god module src/vallm/cli.py (895L, 0 classes) | high | high |
| 2 | Split validate (CC=18 → target CC<10) | medium | low |
| 3 | Split _show_file_details (CC=15 → target CC<10) | medium | low |
| 4 | Split _output_batch_rich (CC=18 → target CC<10) | medium | low |
| 5 | Reduce validate fan-out (currently 21) | medium | medium |
| 6 | Reduce SemanticValidator._parse_response fan-out (currently 17) | medium | medium |

## Context for LLM

When suggesting changes:
1. Start from hotspots and high-CC functions
2. Follow refactoring priorities above
3. Maintain public API surface — keep backward compatibility
4. Prefer minimal, incremental changes

