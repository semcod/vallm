# System Architecture Analysis

## Overview

- **Project**: vallm
- **Language**: python
- **Files**: 16
- **Lines**: 4170
- **Functions**: 91
- **Classes**: 19
- **Avg CC**: 4.3
- **Critical (CC≥10)**: 8

## Architecture

### root/ (1 files, 14L, 0 functions)

- `project.sh` — 14L, 0 methods, CC↑0

### scripts/ (1 files, 78L, 2 functions)

- `bump_version.py` — 78L, 2 methods, CC↑5

### src/vallm/ (6 files, 707L, 16 functions)

- `cli.py` — 401L, 8 methods, CC↑42
- `scoring.py` — 191L, 4 methods, CC↑7
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

### src/vallm/validators/ (7 files, 1456L, 43 functions)

- `complexity.py` — 183L, 4 methods, CC↑12
- `semantic.py` — 249L, 8 methods, CC↑12
- `imports.py` — 653L, 22 methods, CC↑10
- `security.py` — 253L, 5 methods, CC↑9
- `syntax.py` — 96L, 3 methods, CC↑4
- _2 more files_

## Key Exports

- **validate** (function, CC=18) ⚠ split
- **batch** (function, CC=42) ⚠ split
- **ComplexityValidator** (class, CC̄=6.8)
- **GitignoreParser** (class, CC̄=5.7)
- **SecurityValidator** (class, CC̄=5.4)

## Hotspots (High Fan-Out)

- **batch** — fan-out=34: Validate multiple files with auto-detected languages.
- **validate** — fan-out=20: Validate a code proposal through the vallm pipeline.
- **SemanticValidator._parse_response** — fan-out=17: Parse LLM JSON response into a ValidationResult.
- **check** — fan-out=12: Quick syntax check only (tier 1).
- **main** — fan-out=11: Orchestrates 11 calls
- **SandboxRunner._run_docker** — fan-out=11: Run code in a Docker container (requires docker package).
- **info** — fan-out=10: Show vallm configuration and available validators.

## Refactoring Priorities

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Split batch (CC=42 → target CC<10) | high | low |
| 2 | Split god module src/vallm/validators/imports.py (653L, 1 classes) | high | high |
| 3 | Split validate (CC=18 → target CC<10) | medium | low |
| 4 | Reduce batch fan-out (currently 34) | medium | medium |
| 5 | Reduce validate fan-out (currently 20) | medium | medium |
| 6 | Reduce SemanticValidator._parse_response fan-out (currently 17) | medium | medium |

## Context for LLM

When suggesting changes:
1. Start from hotspots and high-CC functions
2. Follow refactoring priorities above
3. Maintain public API surface — keep backward compatibility
4. Prefer minimal, incremental changes

