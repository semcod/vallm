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
- CONTRIBUTING.md

### Added (Multi-Language Support)
- **Language enum** — 30+ programming languages with metadata (compiled/scripting/web)
- **Auto-detection** — detect language from file path, extension, or name
- **`vallm.core.languages`** — centralized language definitions and utilities
- **CLI auto-detection** — `vallm validate --file script.py` auto-detects Python
- **`vallm batch`** command — validate multiple files with mixed languages
- **Lizard integration** — complexity analysis for 16+ languages (Go, Rust, Java, C/C++, etc.)
- **Tree-sitter for all** — syntax validation for 165+ languages
- **Example 07** — comprehensive multi-language demo with 8 languages

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

Last updated: 2026-03-01