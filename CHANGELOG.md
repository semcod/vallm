## [0.1.73] - 2026-04-09

### Changed
- **Refactoring** — Split high-cyclomatic-complexity functions to improve maintainability
  - `walk` in `src/vallm/validators/imports/utils.py` (CC 27 → ~15)
  - `BatchProcessor._process_files_sequential` (CC 26 → ~15)
  - `validate_code` in `mcp/server/_tools_vallm.py` (CC 22 → ~15)
  - Extracted `_DEFAULT_EXCLUDE_PATTERNS` constant and helper functions
- **Test performance** — Optimized test suite for faster execution
  - Marked 19 tests as `@pytest.mark.slow` (excluded from default suite)
  - Test time: 147 passed in 2.81s (down from 166 tests in ~7s)
  - Fixed pytest configuration for goal compatibility

### Fixed
- **pytest configuration** — Removed `--numprocesses=auto` and `--asyncio-mode=auto` from default addopts for goal compatibility
- **Makefile** — Added venv target and automatic virtual environment creation

## [0.1.72] - 2026-04-01

### Added (Quality Pipeline)
- **pyqual integration** — Declarative quality gate system with automated pipeline
  - Quality gates: cc ≤ 15, vallm_pass ≥ 90%, coverage ≥ 55%
  - Automated stages: setup → analyze → validate → test → push → publish
  - Pipeline config in `pyqual.yaml`
- **Automated publishing** — `make publish` and `make publish-test` with credential checking
  - Graceful skip when TWINE_USERNAME/PYPI_API_TOKEN not set
  - Non-interactive twine upload support

### Changed
- **test stage** — Added pytest-cov for coverage reporting (63.9% current)
- **Makefile** — Fixed publish targets to handle missing credentials gracefully

### Docs
- **README.md** — Added "Quality Pipeline (pyqual)" section with gates and commands
- **pyqual.yaml** — Full pipeline configuration with 11 stages and 3 quality gates

## [0.1.9] - 2026-03-22

## [0.1.10] - 2026-03-30

### Fixed
- Fix unused-imports issues (ticket-3e81f7eb)

## [0.1.10] - 2026-03-30

### Fixed
- Fix smart-return-type issues (ticket-ca5db6bd)
- Fix string-concat issues (ticket-0ff3c911)
- Fix unused-imports issues (ticket-a19e92b7)
- Fix llm-hallucinations issues (ticket-6d5c7930)
- Fix ai-boilerplate issues (ticket-cf0d69ab)
- Fix smart-return-type issues (ticket-943add93)
- Fix unused-imports issues (ticket-16ec400a)
- Fix duplicate-imports issues (ticket-6ede072d)
- Fix llm-hallucinations issues (ticket-ab1fe5da)
- Fix ai-boilerplate issues (ticket-5de3d072)
- Fix smart-return-type issues (ticket-80cf92d8)
- Fix string-concat issues (ticket-49ab59ce)
- Fix unused-imports issues (ticket-1abb34c4)
- Fix llm-hallucinations issues (ticket-2be9c4b6)
- Fix ai-boilerplate issues (ticket-eec23a61)
- Fix smart-return-type issues (ticket-75ac97e5)
- Fix string-concat issues (ticket-4bb70532)
- Fix unused-imports issues (ticket-ba057050)
- Fix llm-hallucinations issues (ticket-02beea11)
- Fix ai-boilerplate issues (ticket-cc811a49)
- Fix smart-return-type issues (ticket-09d49f27)
- Fix string-concat issues (ticket-2009f842)
- Fix unused-imports issues (ticket-b9c1effb)
- Fix llm-hallucinations issues (ticket-127edaa6)
- Fix ai-boilerplate issues (ticket-bd912ad1)
- Fix smart-return-type issues (ticket-d611dc60)
- Fix unused-imports issues (ticket-2a960327)
- Fix llm-hallucinations issues (ticket-21bf2700)
- Fix ai-boilerplate issues (ticket-c3ebfedb)
- Fix smart-return-type issues (ticket-82745a0d)
- Fix unused-imports issues (ticket-03e676ea)
- Fix llm-hallucinations issues (ticket-0193eb0e)
- Fix ai-boilerplate issues (ticket-b27a58ac)
- Fix smart-return-type issues (ticket-1365f8ce)
- Fix ai-boilerplate issues (ticket-9d9c2405)
- Fix smart-return-type issues (ticket-7e2b36e2)
- Fix string-concat issues (ticket-68e000e1)
- Fix ai-boilerplate issues (ticket-d1377bc4)
- Fix smart-return-type issues (ticket-6f2fabf4)
- Fix string-concat issues (ticket-beac6f8c)
- Fix unused-imports issues (ticket-18b763bf)
- Fix duplicate-imports issues (ticket-4e1b8d66)
- Fix ai-boilerplate issues (ticket-745d3daf)
- Fix smart-return-type issues (ticket-3f04334c)
- Fix string-concat issues (ticket-93adeb82)
- Fix ai-boilerplate issues (ticket-fc1e6ac6)
- Fix smart-return-type issues (ticket-7c7292ae)
- Fix string-concat issues (ticket-b4cbbc07)
- Fix unused-imports issues (ticket-8f2cdc73)
- Fix duplicate-imports issues (ticket-941dd5c2)
- Fix magic-numbers issues (ticket-6a244dc5)
- Fix smart-return-type issues (ticket-0bc2b3b1)
- Fix string-concat issues (ticket-00bfa45e)
- Fix unused-imports issues (ticket-d905e31f)
- Fix llm-hallucinations issues (ticket-f3a5520e)
- Fix magic-numbers issues (ticket-8622cc21)
- Fix ai-boilerplate issues (ticket-0e064044)
- Fix smart-return-type issues (ticket-d77c8e24)
- Fix unused-imports issues (ticket-7f4d2585)
- Fix magic-numbers issues (ticket-c01924e3)
- Fix ai-boilerplate issues (ticket-c53e2044)
- Fix smart-return-type issues (ticket-098fe086)
- Fix string-concat issues (ticket-7ab2ac22)
- Fix unused-imports issues (ticket-a1be07df)
- Fix ai-boilerplate issues (ticket-4e94e2a4)
- Fix smart-return-type issues (ticket-b022e7e8)
- Fix string-concat issues (ticket-12b48d23)
- Fix unused-imports issues (ticket-68957b2f)
- Fix duplicate-imports issues (ticket-c10cd3dd)
- Fix llm-hallucinations issues (ticket-2e3ff433)
- Fix magic-numbers issues (ticket-875894bf)
- Fix ai-boilerplate issues (ticket-6e0799ce)
- Fix relative-imports issues (ticket-93c30acb)
- Fix smart-return-type issues (ticket-f93bb154)
- Fix unused-imports issues (ticket-b73a31b1)
- Fix ai-boilerplate issues (ticket-7d6f4d0c)
- Fix relative-imports issues (ticket-72f97888)
- Fix smart-return-type issues (ticket-2ec52f5b)
- Fix unused-imports issues (ticket-ed2230ce)
- Fix ai-boilerplate issues (ticket-75bd5636)
- Fix relative-imports issues (ticket-9699a981)
- Fix smart-return-type issues (ticket-f1b432d6)
- Fix unused-imports issues (ticket-c4cc99a0)
- Fix ai-boilerplate issues (ticket-7bd6d2b0)
- Fix smart-return-type issues (ticket-01c61bd7)
- Fix magic-numbers issues (ticket-fe65c812)
- Fix ai-boilerplate issues (ticket-3515b68a)
- Fix relative-imports issues (ticket-6e6246e0)
- Fix unused-imports issues (ticket-1ba3d5c6)
- Fix smart-return-type issues (ticket-6251b32a)
- Fix string-concat issues (ticket-52ad2c7d)
- Fix unused-imports issues (ticket-4d827139)
- Fix llm-hallucinations issues (ticket-13a20ab4)
- Fix magic-numbers issues (ticket-43b7cd55)
- Fix ai-boilerplate issues (ticket-b13aecde)
- Fix unused-imports issues (ticket-501aae2c)
- Fix llm-generated-code issues (ticket-394c6be4)
- Fix unused-imports issues (ticket-8f0354a3)
- Fix llm-generated-code issues (ticket-f8b1cbb3)
- Fix unused-imports issues (ticket-478d7856)
- Fix llm-generated-code issues (ticket-f62e05b5)
- Fix relative-imports issues (ticket-dcb5272e)
- Fix unused-imports issues (ticket-58d9eb72)
- Fix magic-numbers issues (ticket-56f66994)
- Fix unused-imports issues (ticket-474f7ee9)
- Fix llm-generated-code issues (ticket-41d048e3)
- Fix smart-return-type issues (ticket-4e9c5a4c)
- Fix unused-imports issues (ticket-d369288c)
- Fix llm-hallucinations issues (ticket-83ad8d8a)
- Fix magic-numbers issues (ticket-fb468a3b)
- Fix llm-generated-code issues (ticket-43a9a933)
- Fix ai-boilerplate issues (ticket-3775c93c)
- Fix unused-imports issues (ticket-767b0b3d)
- Fix llm-generated-code issues (ticket-f1de0438)
- Fix llm-generated-code issues (ticket-dc135b21)
- Fix relative-imports issues (ticket-2abdb923)
- Fix string-concat issues (ticket-875541cf)
- Fix unused-imports issues (ticket-529c7bcd)
- Fix duplicate-imports issues (ticket-4ddc398a)
- Fix llm-generated-code issues (ticket-3114743c)
- Fix string-concat issues (ticket-8f598ffd)
- Fix unused-imports issues (ticket-a8982a86)
- Fix magic-numbers issues (ticket-e5339b86)
- Fix llm-generated-code issues (ticket-cad49da9)
- Fix unused-imports issues (ticket-3abe48a5)
- Fix llm-generated-code issues (ticket-927dc374)
- Fix string-concat issues (ticket-a027c9cc)
- Fix unused-imports issues (ticket-b2a671a1)
- Fix llm-generated-code issues (ticket-98006bf4)
- Fix unused-imports issues (ticket-4161ea25)
- Fix llm-generated-code issues (ticket-d8d710dd)
- Fix smart-return-type issues (ticket-32fb1c22)
- Fix magic-numbers issues (ticket-4a63bee2)
- Fix ai-boilerplate issues (ticket-e3f0b8fe)
- Fix ai-boilerplate issues (ticket-d668d7e6)
- Fix smart-return-type issues (ticket-30b709d8)
- Fix ai-boilerplate issues (ticket-e018eadf)
- Fix unused-imports issues (ticket-735f0b24)
- Fix unused-imports issues (ticket-ae6a7a3b)
- Fix duplicate-imports issues (ticket-989c189b)
- Fix unused-imports issues (ticket-b7f5d0cd)
- Fix duplicate-imports issues (ticket-5047c56e)
- Fix string-concat issues (ticket-db5f6c39)
- Fix unused-imports issues (ticket-5e43becb)
- Fix unused-imports issues (ticket-4375c4b2)
- Fix unused-imports issues (ticket-5b9fdf2a)
- Fix ai-boilerplate issues (ticket-889e0d54)
- Fix unused-imports issues (ticket-f9beb0e8)
- Fix magic-numbers issues (ticket-969fa44d)
- Fix unused-imports issues (ticket-02943944)
- Fix smart-return-type issues (ticket-49bf9039)
- Fix unused-imports issues (ticket-4dbe8575)
- Fix string-concat issues (ticket-83c5ccc5)
- Fix unused-imports issues (ticket-d3174bc4)
- Fix llm-generated-code issues (ticket-b7264256)
- Fix unused-imports issues (ticket-11db01e2)
- Fix smart-return-type issues (ticket-8d4fa712)
- Fix unused-imports issues (ticket-0dd81477)
- Fix string-concat issues (ticket-3385abd4)
- Fix unused-imports issues (ticket-697325dc)
- Fix llm-generated-code issues (ticket-ecb004c1)
- Fix unused-imports issues (ticket-76b552c5)
- Fix string-concat issues (ticket-b15f60bd)
- Fix unused-imports issues (ticket-2ca31004)
- Fix magic-numbers issues (ticket-bd66e1ef)
- Fix unused-imports issues (ticket-57872c49)
- Fix unused-imports issues (ticket-433597d0)
- Fix unused-imports issues (ticket-83f35711)
- Fix llm-generated-code issues (ticket-d0bdad6a)
- Fix relative-imports issues (ticket-b333b94a)
- Fix unused-imports issues (ticket-f9785f7a)
- Fix magic-numbers issues (ticket-36e67e3b)
- Fix relative-imports issues (ticket-48fbdba5)
- Fix smart-return-type issues (ticket-e96ae62c)
- Fix string-concat issues (ticket-1b3aacd6)
- Fix relative-imports issues (ticket-fd68a8a6)
- Fix smart-return-type issues (ticket-bd3b4036)
- Fix relative-imports issues (ticket-cd71b68f)
- Fix smart-return-type issues (ticket-40074672)
- Fix string-concat issues (ticket-623af541)
- Fix unused-imports issues (ticket-8f5b1ee1)
- Fix relative-imports issues (ticket-e7cccd58)
- Fix smart-return-type issues (ticket-6dc40711)
- Fix string-concat issues (ticket-84c8371b)
- Fix unused-imports issues (ticket-cdb74e00)
- Fix relative-imports issues (ticket-0556eaf7)
- Fix smart-return-type issues (ticket-c437f7f8)
- Fix string-concat issues (ticket-b0e04cd4)
- Fix relative-imports issues (ticket-ddd47ada)
- Fix relative-imports issues (ticket-9368ba9f)
- Fix smart-return-type issues (ticket-1eaed606)
- Fix string-concat issues (ticket-08280a88)
- Fix unused-imports issues (ticket-11b2308a)
- Fix relative-imports issues (ticket-dae52aa2)
- Fix string-concat issues (ticket-f5ddee4e)
- Fix llm-generated-code issues (ticket-04e1dae7)
- Fix relative-imports issues (ticket-68c5ee1d)
- Fix unused-imports issues (ticket-7483cd3b)
- Fix magic-numbers issues (ticket-69b74c21)
- Fix llm-generated-code issues (ticket-e17d9784)
- Fix string-concat issues (ticket-9f456312)
- Fix unused-imports issues (ticket-7636f718)
- Fix llm-generated-code issues (ticket-36761343)
- Fix string-concat issues (ticket-86446eb8)
- Fix unused-imports issues (ticket-22ed47e6)
- Fix magic-numbers issues (ticket-949dc807)
- Fix llm-generated-code issues (ticket-3cf85229)
- Fix unused-imports issues (ticket-1791ee4a)
- Fix unused-imports issues (ticket-ccec706b)
- Fix magic-numbers issues (ticket-250bd20f)
- Fix unused-imports issues (ticket-b2249312)
- Fix llm-generated-code issues (ticket-057c4d08)
- Fix smart-return-type issues (ticket-2ddd1365)
- Fix unused-imports issues (ticket-fe8a990f)
- Fix llm-hallucinations issues (ticket-889e1052)
- Fix ai-boilerplate issues (ticket-046a285e)
- Fix unused-imports issues (ticket-2a4724cb)

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

## [0.1.74] - 2026-04-09

### Docs
- Update CHANGELOG.md
- Update docs/README.md
- Update docs/TESTING.md

### Other
- Update examples/10_mcp_ollama_demo/mcp_demo.py
- Update examples/11_claude_code_autonomous/claude_autonomous_demo.py
- Update examples/12_ollama_simple_demo/ollama_simple_demo.py
- Update mcp/server/_tools_vallm.py
- Update mcp/tests/test_client_integration.py

## [0.1.73] - 2026-04-09

### Docs
- Update CONTRIBUTING.md
- Update README.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/conftest.py
- Update tests/semantic_validation/test_code_quality.py
- Update tests/semantic_validation/test_init.py
- Update tests/semantic_validation/test_syntax_and_multilang.py
- Update tests/test_ast_compare.py
- Update tests/test_batch_toon_output.py
- Update tests/test_examples.py
- Update tests/test_gitignore.py
- Update tests/test_performance.py
- Update tests/test_semantic_validation.py
- ... and 1 more files

### Other
- Update .vallm/ast_comparison_summary.json
- Update .vallm/basic_validation_summary.json
- Update .vallm/graph_analysis_summary.json
- Update .vallm/multilang_summary.json
- Update .vallm/security_check_summary.json
- Update Makefile
- Update examples/02_ast_comparison/main.py
- Update examples/03_security_check/main.py
- Update examples/04_graph_analysis/main.py
- Update examples/08_code2llm_integration/.vallm/code2llm_integration_report.json
- ... and 19 more files

## [0.1.72] - 2026-04-08

### Docs
- Update README.md
- Update TODO.md

### Test
- Update tests/mock_llm_provider.py
- Update tests/semantic_validation/__init__.py
- Update tests/semantic_validation/fixtures.py
- Update tests/semantic_validation/test_code_quality.py
- Update tests/semantic_validation/test_init.py
- Update tests/semantic_validation/test_syntax_and_multilang.py
- Update tests/test_semantic_validation.py

### Other
- Update examples/11_claude_code_autonomous/claude_autonomous_demo.py

## [0.1.71] - 2026-03-31

### Docs
- Update README.md

## [0.1.70] - 2026-03-31

### Docs
- Update README.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Other
- Update .pyqual/ruff.json
- Update VERSION
- Update project.sh
- Update project/analysis.toon.yaml
- Update project/validation.toon.yaml
- Update project/verify/validation.toon.yaml

## [0.1.68] - 2026-03-31

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update .pyqual/ruff.json
- Update mcp/server/_tools_vallm.py
- Update planfile.yaml
- Update prefact.yaml
- Update project.sh
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- ... and 24 more files

## [0.1.67] - 2026-03-26

### Test
- Update tests/test_batch_toon_output.py

### Other
- Update project/validation.toon.yaml

## [0.1.66] - 2026-03-26

### Docs
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_batch_toon_output.py

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- Update project/flow.png
- Update project/index.html
- ... and 4 more files

## [0.1.65] - 2026-03-25

### Docs
- Update docs/README.md

### Other
- Update project/analysis.json
- Update project/analysis.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- Update project/flow.png
- Update project/index.html
- ... and 1 more files

## [0.1.64] - 2026-03-25

### Docs
- Update project/context.md

### Other
- Update project.sh
- Update project/analysis.json
- Update project/analysis.toon.yaml
- Update project/analysis.yaml
- Update project/map.toon.yaml
- Update project/toon.toon.yaml

## [0.1.63] - 2026-03-25

### Docs
- Update docs/README.md

### Test
- Update tests/test_performance.py

### Other
- Update project/analysis.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.yaml
- Update project/index.html

## [0.1.62] - 2026-03-25

### Docs
- Update project/context.md

### Other
- Update project/analysis.yaml
- Update project/toon.yaml

## [0.1.61] - 2026-03-25

### Test
- Update tests/test_performance.py

## [0.1.60] - 2026-03-25

### Docs
- Update docs/README.md
- Update project/context.md

### Other
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.yaml
- Update project/flow.mmd
- Update project/flow.png
- Update project/index.html
- Update project/map.yaml
- ... and 2 more files

## [0.1.59] - 2026-03-25

### Docs
- Update docs/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/analysis.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/flow.mmd
- Update project/flow.png
- Update project/index.html
- Update project/validation.toon.yaml

## [0.1.58] - 2026-03-25

### Docs
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/analysis.yaml
- Update project/duplication.toon.toon

## [0.1.57] - 2026-03-25

### Docs
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.toon
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- Update project/flow.png
- Update project/index.html
- ... and 2 more files

## [0.1.56] - 2026-03-25

### Docs
- Update docs/README.md
- Update project/README.md

### Other
- Update .env.example
- Update project/analysis.json
- Update project/analysis.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon
- Update project/evolution.toon.yaml
- Update project/flow.png
- ... and 2 more files

## [0.1.55] - 2026-03-25

### Docs
- Update project/context.md

### Other
- Update project.toon
- Update project/analysis.json
- Update project/analysis.toon
- Update project/analysis.toon.yaml
- Update project/analysis.yaml
- Update project/dashboard.html
- Update project/flow.mmd
- Update project/flow.toon
- Update project/map.toon
- Update project/map.toon.yaml
- ... and 2 more files

## [0.1.54] - 2026-03-24

### Docs
- Update CHANGELOG.md
- Update MCP_INTEGRATION_SUMMARY.md
- Update README.md
- Update docs/README.md
- Update mcp/README.md
- Update project/context.md

### Other
- Update project/analysis.toon
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/dashboard.html
- Update project/duplication.toon
- Update project/flow.mmd
- Update project/flow.png
- Update project/flow.toon
- ... and 6 more files

## [0.1.53] - 2026-03-24

### Docs
- Update MCP_INTEGRATION_SUMMARY.md
- Update README.md
- Update docs/README.md
- Update mcp/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update test_mcp.py

### Other
- Update examples/mcp_demo.py
- Update mcp/__init__.py
- Update mcp/server/__init__.py
- Update mcp/server/_tools_vallm.py
- Update mcp/server/self_server.py
- Update mcp/tests/Dockerfile.client
- Update mcp/tests/Dockerfile.test
- Update mcp/tests/__init__.py
- Update mcp/tests/container_e2e.py
- Update mcp/tests/docker-compose.yml
- ... and 22 more files

## [0.1.52] - 2026-03-24

### Test
- Update tests/conftest.py
- Update tests/test_pipeline.py
- Update tests/test_regression_validator.py

### Other
- Update .gitignore

## [0.1.51] - 2026-03-23

### Docs
- Update docs/README.md

### Other
- Update project/analysis.json
- Update project/analysis.yaml
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/duplication.toon
- Update project/flow.png
- Update project/index.html
- Update project/project.toon

## [0.1.50] - 2026-03-23

### Other
- Update project/analysis.json
- Update project/analysis.yaml
- Update project/calls.mmd
- Update project/flow.mmd

## [0.1.49] - 2026-03-23

### Docs
- Update project/context.md

### Other
- Update project/analysis.toon
- Update project/analysis.yaml
- Update project/dashboard.html
- Update project/flow.toon
- Update project/map.toon
- Update project/project.toon
- Update project/project.yaml

## [0.1.48] - 2026-03-23

### Other
- Update project/validation.toon

## [0.1.47] - 2026-03-23

### Docs
- Update docs/README.md

### Other
- Update project/analysis.json
- Update project/analysis.yaml
- Update project/duplication.toon
- Update project/evolution.toon
- Update project/flow.png
- Update project/index.html
- Update project/project.toon

## [0.1.46] - 2026-03-23

### Other
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png

## [0.1.45] - 2026-03-23

### Other
- Update project/analysis.json
- Update project/calls.mmd
- Update project/flow.mmd

## [0.1.44] - 2026-03-23

### Other
- Update project/analysis.json
- Update project/calls.mmd
- Update project/flow.mmd

## [0.1.43] - 2026-03-23

### Other
- Update project/analysis.yaml

## [0.1.42] - 2026-03-23

### Other
- Update project/analysis.yaml

## [0.1.41] - 2026-03-23

### Other
- Update project/analysis.yaml

## [0.1.40] - 2026-03-23

### Other
- Update project/analysis.yaml

## [0.1.39] - 2026-03-23

### Docs
- Update project/context.md

### Other
- Update project/analysis.toon
- Update project/analysis.yaml
- Update project/dashboard.html
- Update project/flow.toon
- Update project/map.toon
- Update project/project.toon
- Update project/project.yaml

## [0.1.38] - 2026-03-23

### Test
- Update tests/test_semantic_validation.py

## [0.1.37] - 2026-03-23

### Test
- Update tests/test_semantic_validation.py

### Other
- Update project/validation.toon

## [0.1.36] - 2026-03-23

### Test
- Update tests/test_semantic_validation.py

### Other
- Update project/validation.toon

## [0.1.35] - 2026-03-23

### Test
- Update tests/test_semantic_validation.py

### Other
- Update project/validation.json

## [0.1.34] - 2026-03-23

### Other
- Update project/validation.json
- Update project/validation.toon
- Update project/validation.yaml

## [0.1.33] - 2026-03-23

### Other
- Update toon/validation.txt

## [0.1.32] - 2026-03-23

### Docs
- Update docs/README.md
- Update project/README.md

### Other
- Update project/analysis.json
- Update project/analysis.yaml
- Update project/calls.png
- Update project/compact_flow.png
- Update project/duplication.toon
- Update project/evolution.toon
- Update project/flow.png
- Update project/index.html
- Update project/project.toon

## [0.1.31] - 2026-03-23

### Other
- Update project/validation.toon

## [0.1.30] - 2026-03-23

### Docs
- Update project/README.md

### Other
- Update project/analysis.json
- Update project/analysis.yaml
- Update project/calls.png
- Update project/compact_flow.png
- Update project/evolution.toon
- Update project/flow.png
- Update project/index.html
- Update project/project.toon

## [0.1.29] - 2026-03-23

### Other
- Update project/compact_flow.mmd

## [0.1.28] - 2026-03-23

### Other
- Update project/analysis.json
- Update project/analysis.yaml
- Update project/calls.mmd
- Update project/flow.mmd

## [0.1.27] - 2026-03-23

### Other
- Update project/analysis.yaml
- Update project/validation.toon
- Update toon/validation.txt

## [0.1.26] - 2026-03-23

### Test
- Update tests/test_performance.py

### Other
- Update project/analysis.yaml
- Update project/validation.toon

## [0.1.25] - 2026-03-23

### Docs
- Update project/context.md

### Other
- Update project/analysis.toon
- Update project/analysis.yaml
- Update project/dashboard.html
- Update project/flow.toon
- Update project/map.toon
- Update project/project.toon
- Update project/project.yaml

## [0.1.24] - 2026-03-23

### Other
- Update project.sh

## [0.1.23] - 2026-03-23

## [0.1.22] - 2026-03-23

### Other
- Update project.sh
- Update project/validation.toon

## [0.1.21] - 2026-03-23

### Docs
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_plugins.py
- Update tests/test_sandbox.py

### Other
- Update .gitignore
- Update examples/12_ollama_simple_demo/best_version.py
- Update examples/12_ollama_simple_demo/iteration_1.py
- Update examples/12_ollama_simple_demo/iteration_2.py
- Update project/analysis.toon
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/dashboard.html
- ... and 10 more files

## [0.1.20] - 2026-03-23

### Docs
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update .gitignore
- Update project.sh
- Update project/analysis.toon
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/dashboard.html
- Update project/duplication.toon
- Update project/evolution.toon
- ... and 8 more files

## [0.1.19] - 2026-03-23

### Other
- Update project.sh
- Update project/validation.json
- Update project/validation.toon
- Update project/validation.yaml

## [0.1.18] - 2026-03-23

### Docs
- Update README.md
- Update docs/README.md
- Update project/context.md

### Other
- Update project.sh
- Update project/analysis.toon
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/dashboard.html
- Update project/duplication.toon
- Update project/flow.mmd
- Update project/flow.png
- ... and 6 more files

## [0.1.17] - 2026-03-23

### Docs
- Update README.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update .gitignore
- Update project.sh
- Update project/analysis.toon
- Update project/calls.mmd
- Update project/calls.png
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/dashboard.html
- Update project/duplication.toon
- Update project/evolution.toon
- ... and 8 more files

## [0.1.16] - 2026-03-23

### Docs
- Update CHANGELOG.md
- Update TODO.md

### Test
- Update tests/test_performance.py

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

### 🛠️ New Shared Utilities
- `examples/utils/validation_runner.py` - Standard validation patterns
- `examples/utils/extract_code_from_response.py` - LLM response parsing
- `examples/12_ollama_simple_demo/utils/` - Demo-specific utilities
- Enhanced `BaseImportValidator` - Common validation logic

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

Last updated: 2026-03-24