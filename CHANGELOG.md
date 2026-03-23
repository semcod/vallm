## [0.1.9] - 2026-03-22

### Summary

docs: comprehensive documentation update with code health metrics and CLI improvements

### Added (CLI)
- **Detailed batch output** — show reasons for failures with validator scores and issues
- **New CLI options for batch**: `--verbose` (-v), `--show-issues` (-i) for detailed per-file results
- **New output formats**: `json`, `yaml`, `toon` for batch results (was: rich, text only)
- **Failed files summary** — list of failed files with scores, issues, and semantic validator summaries

### Docs
- docs: add code health metrics section to README (CC̄=3.5, max-CC=42, god modules=2)
- docs: document critical functions requiring refactoring (batch CC=42, validate CC=18)
- docs: add god modules inventory (imports.py 653L, cli.py 401L)
- docs: create CONTRIBUTING.md with development guidelines
- docs: update TODO.md with prioritized refactoring queue (4 priority levels)
- docs: update example list in README (12 examples including MCP and Ollama demos)

### Analysis
- analysis: generate code2llm analysis files (analysis.toon, evolution.toon, context.md)
- metrics: 91 functions, 19 classes, 56 modules, 8 critical functions (CC≥10)

---

## [0.1.8] - 2026-03-01

### Summary

fix(examples): configuration management system

### Docs

- docs: update README

### Other

- docker: update Dockerfile
- update examples/11_claude_code_autonomous/claude_autonomous_demo.py
- scripts: update docker-entrypoint.sh
- update examples/11_claude_code_autonomous/legacy_code/data_processor.py
- update examples/11_claude_code_autonomous/requirements.txt
- scripts: update run.sh
- docker: update Dockerfile
- scripts: update docker-entrypoint.sh
- update examples/12_ollama_simple_demo/legacy_code/simple_buggy.py
- update examples/12_ollama_simple_demo/ollama_simple_demo.py
- ... and 2 more


## [0.1.7] - 2026-03-01

### Summary

refactor(examples): configuration management system

### Other

- update examples/10_mcp_ollama_demo/mcp_demo.py
- update examples/10_mcp_ollama_demo/refactored_output.py


## [0.1.6] - 2026-03-01

### Summary

feat(build): commit message generator

### Ci

- config: update ci.yml
- config: update publish.yml

### Other

- config: update .pre-commit-config.yaml


## [0.1.5] - 2026-03-01

### Added
- **.gitignore support** — `vallm batch` respects `.gitignore` patterns with `--use-gitignore` flag (default: true)
- **30+ languages** — expanded Language enum with Zig, Dart, Crystal, Nim, V, Julia, Clojure, F#, Gleam, WebAssembly, Cairo, Noir, Circom, Sway, and more
- **Gitignore parser** — full support for directory patterns, negations, glob patterns
- **Tests** — 13 tests for gitignore, 39 tests for language detection (52 total)
- **Examples 08 & 09** — integration examples with code2llm and code2logic packages
- **Language metadata** — `is_compiled`, `is_scripting`, `is_web` properties for each language

### Changed
- **CLI `batch` command** — added `--use-gitignore/--no-gitignore` flag
- **Language detection** — improved auto-detection for 30+ file extensions
- **project.sh** — prepared for vallm batch validation integration


# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Refactor 5 critical-CC functions (target max-CC ≤7)
- Wire pluggy plugin manager for entry_point-based validator discovery
- Add LogicalErrorValidator (pyflakes), LintValidator (ruff), TypeCheckValidator (mypy)
- Add RegressionValidator (Tier 4) with pytest-json-report
- Integrate apted/zss for AST edit distance scoring
- Add CodeBERTScore embedding similarity to SemanticValidator
- NetworkX graph analysis (cycle detection, centrality)
- TOML config loading, `[tool.vallm]` support
- Pre-commit hook integration
- GitHub Actions CI/CD pipeline

### Added (Multi-Language Support)
- **Language enum** — 30+ programming languages with metadata (compiled/scripting/web)
- **Auto-detection** — detect language from file path, extension, or name
- **`vallm.core.languages`** — centralized language definitions and utilities
- **CLI auto-detection** — `vallm validate --file script.py` auto-detects Python
- **`vallm batch`** command — validate multiple files with mixed languages
- **Lizard integration** — complexity analysis for 16+ languages (Go, Rust, Java, C/C++, etc.)
- **Tree-sitter for all** — syntax validation for 165+ languages
- **Example 07** — comprehensive multi-language demo with 8 languages

## [0.1.12] - 2026-03-23

### Docs
- Update CHANGELOG.md
- Update README.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/dashboard.html
- Update project/duplication.toon
- Update project/evolution.toon
- Update project/flow.mmd
- Update project/flow.png
- ... and 6 more files

## [0.1.11] - 2026-03-23

### 🚀 Major Refactoring Release

**BREAKING CHANGES**: None - 100% backward compatibility maintained

### ✅ CLI Modularization
- **Split CLI god module** - Refactored 850-line `cli.py` into focused package:
  - `cli/__init__.py` - Command registration and app export (33L)
  - `cli/command_handlers.py` - CLI command implementations (280L)
  - `cli/output_formatters.py` - Output formatting utilities (280L)
  - `cli/settings_builders.py` - Settings configuration logic (35L)
  - `cli/batch_processor.py` - Batch processing logic (320L)
  - `cli.py` - Simplified main entry point (9L)
- **Maintained compatibility** - All existing CLI commands and options preserved
- **Improved maintainability** - Single responsibility principle applied

### ✅ Import Validator Cleanup
- **Removed legacy module** - Deleted `validators/imports_original.py` (653L)
- **Enhanced base class** - `BaseImportValidator` with shared validation logic
- **Template method pattern** - Eliminated duplicate `validate()` methods
- **Language validators** - Go, Rust, Java now use shared validation infrastructure

### ✅ Code Deduplication (469 lines eliminated)
- **Validation runners** - Extracted 77-line main function duplication (154 lines saved)
- **Analysis data saving** - Centralized `save_analysis_data` function (66 lines saved)
- **Demo utilities** - Shared ollama demo patterns (60 lines saved)
- **LLM response parsing** - Common `extract_code_from_response` function (40 lines saved)
- **Import validation** - Consolidated validator logic (40 lines saved)
- **Additional utilities** - Process_user_input, calculate_total, etc. (109 lines saved)

### 📊 Code Quality Improvements
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| God Modules (>500L) | 2 | 0 | ✅ **100% eliminated** |
| Max Cyclomatic Complexity | 42 | ~18 | ✅ **57% reduction** |
| Code Duplication | 504 lines | 35 lines | ✅ **93% eliminated** |
| CLI Module Size | 850 lines | 9 lines | ✅ **99% reduction** |

### 🛠️ New Validators
- **LogicalErrorValidator** — Tier 1: pyflakes integration for detecting logical errors and unused imports
- **LintValidator** — Tier 1: ruff integration for style and lint checks with JSON output
- **SemanticCache** — Caching layer for semantic validation results to improve performance

### 🛠️ New Shared Utilities
- `examples/utils/validation_runner.py` - Standard validation patterns
- `examples/utils/extract_code_from_response.py` - LLM response parsing
- `examples/12_ollama_simple_demo/utils/` - Demo-specific utilities
- Enhanced `BaseImportValidator` - Common validation logic

### 🧪 New Test Suites
- **test_sandbox.py** — Comprehensive sandbox runner tests (8 test cases)
- **test_plugins.py** — Plugin system tests for pluggy integration (8 test cases)
- **test_performance.py** — Performance and load testing (12 test cases)
- Enhanced test coverage in existing test files

### 📚 Documentation Updates
- **README.md** - Updated architecture section with new modular structure
- **TODO.md** - Marked major refactoring tasks as completed
- **Code health metrics** - Added comprehensive improvement statistics

---

## [0.1.10] - 2026-03-23

### Docs
- Update CHANGELOG.md
- Update README.md
- Update code2llm_output/README.md
- Update code2llm_output/context.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_cli_e2e.py
- Update tests/test_imports.py
- Update tests/test_installation.py
- Update tests/test_semantic_validation.py

### Other
- Update code2llm_output/analysis.toon
- Update examples/11_claude_code_autonomous/claude_autonomous_demo.py
- Update project.sh
- Update project/analysis.toon
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/dashboard.html
- Update project/duplication.toon
- ... and 10 more files

## [0.1.9] - 2026-03-22

### Docs
- Update CHANGELOG.md

## [0.1.3] - 2026-03-01

### Added
- **Full package implementation** — 4-tier validation pipeline
- **SyntaxValidator** (Tier 1) — ast.parse + tree-sitter for 165+ languages
- **ImportValidator** (Tier 1) — module resolution with stdlib awareness
- **ComplexityValidator** (Tier 2) — radon (Python CC, MI) + lizard (16 languages)
- **SecurityValidator** (Tier 2) — regex patterns + AST-based eval/exec detection + optional bandit
- **SemanticValidator** (Tier 3) — LLM-as-judge via Ollama, litellm, or direct HTTP
- **Scoring engine** — weighted scores, confidence, hard gates, PASS/REVIEW/FAIL verdict
- **CLI** — `vallm validate`, `vallm check`, `vallm info` with rich/json/text output
- **Config** — pydantic-settings with `VALLM_*` env vars
- **Pluggy hookspecs** — extension points for custom validators
- **Sandbox** — subprocess and Docker backends for safe code execution
- **Code graph analysis** — import/call graph building and structural diffing
- **AST comparison** — tree-sitter node counting, Python AST normalization and similarity
- **6 examples** — basic validation, AST comparison, security, graph analysis, LLM review, multi-language
- **45 unit tests** — all passing
- **Published to PyPI** as `vallm` v0.1.3

### Tested
- Validated with local Ollama + Qwen 2.5 Coder 7B
- LLM correctly identified off-by-one bugs in binary search
- Multi-language validation (Python, JavaScript, C) working

## [0.1.1] - 2026-03-01

### Added
- Initial project scaffolding — pyproject.toml, src layout, hookspecs, config
- Core data models: Proposal, ValidationResult, PipelineResult
- AST comparison utilities (tree-sitter + Python ast)
- Graph builder and diff modules
- Base validator interface

---

Last updated: 2026-03-23