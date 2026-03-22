# TODO

## Refactoring — reduce complexity (current status: 2026-03-22)

**Current Metrics (from code2llm analysis):**
- CC̄ = 3.5 (target: ≤2.4)
- Max CC = 42 (target: ≤20)
- God modules = 2 (target: 0)
- High CC (≥15) = 2 functions (target: ≤1)
- Critical functions (CC≥10) = 8 functions

**Priority 1: Critical Functions (CC≥15)**

- [ ] **`cli.batch` CC=42, fan=34** — SPLIT: extract file discovery, filtering, validation loop, result aggregation, and output formatting into separate modules
- [ ] **`scoring.validate` CC=18, fan=20** — REFACTOR: extract validator sorting and fail-fast execution logic

**Priority 2: High Complexity (CC 10-15)**

- [ ] **`SemanticValidator._parse_response` CC=12, fan=17** — split JSON extraction, score normalization, and issue parsing into 3 methods
- [ ] **`ComplexityValidator._check_python_complexity` CC=11** — extract radon block analysis and MI check into helpers
- [ ] **`_output_rich` CC=11, fan=8** — extract verdict panel, results table, and issues list into separate renderers
- [ ] **`ImportValidator._validate_python` CC=10, fan=13** — extract AST walking into `_extract_imports()` generator
- [ ] **`cli.validate` CC=high** — extract settings build, proposal build, and output dispatch

**Priority 3: God Modules**

- [ ] **`validators/imports.py` (653L, 22 methods)** — SPLIT into language-specific submodules: python.py, javascript.py, go.py, rust.py, java.py, c_cpp.py
  - Risk: 22 import paths depend on this — maintain backward compatibility via `__init__.py` re-exports
- [ ] **`cli.py` (401L, 8 methods, CC=42)** — SPLIT: extract output formatters to `output.py`, batch logic to `batch.py`

**Priority 4: Medium Complexity (CC 5-10)** — 19 functions to review after critical ones

## Multi-Language Support (Completed ✓)

- [x] **Language enum** — 30+ languages with compiled/scripting/web classification
- [x] **Auto-detection** — `detect_language()` from file path, extension, or name
- [x] **`vallm.core.languages`** — centralized language module with LIZARD_SUPPORTED
- [x] **CLI auto-detection** — `validate` and `check` commands auto-detect from file
- [x] **`vallm batch` command** — validate multiple files with mixed languages
- [x] **Complexity for 16+ langs** — lizard integration for Go, Rust, Java, C/C++, etc.
- [x] **Example 07** — comprehensive multi-language demo
- [ ] **Language-specific security patterns** — currently only Python patterns
- [ ] **More language examples** — add Kotlin, Swift, PHP samples

## Missing validators (from spec)

- [ ] **LogicalErrorValidator (Tier 1)** — integrate `pyflakes` (already a dependency, not wired up)
- [ ] **LintValidator (Tier 1)** — integrate `ruff` for style/lint checks via subprocess JSON output
- [ ] **RegressionValidator (Tier 4)** — test execution + result comparison via `pytest-json-report`
- [ ] **TypeCheckValidator (Tier 2)** — `mypy`/`pyright` as optional fast correctness signal

## Missing features (from spec)

- [ ] **Plugin manager wiring** — pluggy hooks are defined in `hookspecs.py` but the `PluginManager` is never instantiated; validators aren't discovered via entry_points
- [ ] **TOML config loading** — `toml_file` was removed from pydantic-settings; implement `TomlConfigSettingsSource` or manual TOML loading
- [ ] **`pyproject.toml [tool.vallm]`** config section support
- [ ] **AST edit distance** — integrate `apted` or `zss` for quantitative tree similarity (spec Section 1)
- [ ] **CodeBERTScore** — wire `code-bert-score` into `SemanticValidator` as an embedding-based score alongside LLM-as-judge
- [ ] **NetworkX graph analysis** — use `networkx` for cycle detection, centrality, and graph edit distance in `graph_diff.py`
- [ ] **Pre-commit hook** — add `.pre-commit-hooks.yaml` so vallm can be used as a pre-commit validator
- [ ] **`hypothesis` / `crosshair`** — property-based test generation for Tier 4
- [ ] **E2B sandbox backend** — cloud Firecracker microVM support via `e2b-code-interpreter`
- [ ] **Streaming LLM output** — show progress during semantic validation
- [ ] **`--fix` / auto-repair mode** — LLM-based automatic fix suggestions with retry loop

## Code quality

- [ ] **Add `py.typed` marker** for PEP 561
- [ ] **Type annotations** — add return types to all public functions; run mypy in CI
- [ ] **Docstrings** — several internal methods lack docstrings
- [ ] **Error handling** — `_diff_list` in `graph_diff.py` crashes on empty lists (edge case)
- [ ] **Tests for semantic validator** — mock Ollama responses, test JSON parsing edge cases
- [ ] **Tests for sandbox runner** — mock subprocess/docker
- [ ] **CLI integration tests** — test `vallm validate`, `vallm check`, `vallm info` via `typer.testing.CliRunner`

## Packaging / CI (Completed ✓)

- [x] **GitHub Actions CI** — pytest + ruff + mypy on Python 3.10–3.13
- [x] **Coverage reporting** — add `pytest-cov` config, badge is currently static 85%
- [x] **Publish automation** — GitHub Actions workflow for PyPI release on tag
- [ ] **CONTRIBUTING.md** — referenced in README badge but doesn't exist

Last updated: 2026-03-01