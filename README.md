# vallm

**A complete toolkit for validating LLM-generated code.**

[![PyPI](https://img.shields.io/pypi/v/vallm)](https://pypi.org/project/vallm/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vallm)](https://pypi.org/project/vallm/)
[![CI](https://github.com/semcod/vallm/workflows/CI/badge.svg)](https://github.com/semcod/vallm/actions)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](https://github.com/semcod/vallm/actions)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue)](https://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-brightgreen)](https://bandit.readthedocs.io/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](https://pre-commit.com/)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/github/codeql-action/init-codeql?label=CodeQL)](https://github.com/semcod/vallm/security)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.1234567-blue)](https://doi.org/10.5281/zenodo.1234567)
[![GitHub stars](https://img.shields.io/github/stars/semcod/vallm?style=social)](https://github.com/semcod/vallm)
[![GitHub forks](https://img.shields.io/github/forks/semcod/vallm?style=social)](https://github.com/semcod/vallm)
[![GitHub issues](https://img.shields.io/github/issues/semcod/vallm)](https://github.com/semcod/vallm/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/semcod/vallm)](https://github.com/semcod/vallm/pulls)
[![Release](https://img.shields.io/github/release/semcod/vallm)](https://github.com/semcod/vallm/releases)
[![Last commit](https://img.shields.io/github/last-commit/semcod/vallm)](https://github.com/semcod/vallm/commits/main)
[![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen)](https://github.com/semcod/vallm)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/semcod/vallm/blob/main/CONTRIBUTING.md)


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.90-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$1.90-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-44.1h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $1.8991 (149 commits)
- 👤 **Human dev:** ~$4411 (44.1h @ $100/h, 30min dedup)

Generated on 2026-05-31 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

vallm validates code proposals through a **four-tier pipeline** — from millisecond syntax checks to LLM-as-judge semantic review — before a single line ships.

## Features

- **Multi-language AST parsing** via tree-sitter (165+ languages)
- **Syntax validation** with ast.parse (Python) and tree-sitter error detection
- **Import resolution** checking for Python, JavaScript/TypeScript, Go, Rust, Java, C/C++
- **Complexity metrics** via radon (Python) and lizard (16 languages)
- **Security scanning** with language-specific patterns and optional bandit integration
- **LLM-as-judge** semantic review via Ollama, litellm, or direct HTTP
- **Code graph analysis** — import/call graph diffing for structural regression detection
- **AST similarity scoring** with normalized fingerprinting
- **Pluggy-based plugin system** for custom validators
- **Rich CLI** with JSON/text output formats
- **MCP integration** — Model Context Protocol server for LLM tool calling

## Supported Languages

| Language | Syntax | Imports | Complexity | Security |
|----------|--------|---------|------------|----------|
| Python | ✅ AST + tree-sitter | ✅ Full resolution (22 methods) | ✅ radon + lizard | ✅ bandit + patterns |
| JavaScript | ✅ tree-sitter | ✅ Node.js builtins | ✅ lizard | ✅ XSS, eval patterns |
| TypeScript | ✅ tree-sitter | ✅ Node.js builtins | ✅ lizard | ✅ XSS, eval patterns |
| Go | ✅ tree-sitter | ✅ stdlib + modules | ✅ lizard | ✅ SQL injection, exec |
| Rust | ✅ tree-sitter | ✅ crates | ✅ lizard | ✅ unsafe, unwrap |
| Java | ✅ tree-sitter | ✅ stdlib packages | ✅ lizard | ✅ Runtime.exec, SQL |
| C/C++ | ✅ tree-sitter | ✅ std headers | ✅ lizard | ✅ buffer overflow, system |
| Ruby | ✅ tree-sitter | ⚠️ Limited | ✅ lizard | ⚠️ Limited |
| PHP | ✅ tree-sitter | ⚠️ Limited | ✅ lizard | ⚠️ Limited |
| Swift | ✅ tree-sitter | ⚠️ Limited | ✅ lizard | ⚠️ Limited |
| Kotlin | ✅ tree-sitter | ⚠️ Limited | ✅ lizard | ⚠️ Limited |
| Scala | ✅ tree-sitter | ⚠️ Limited | ✅ lizard | ⚠️ Limited |

## Installation

```bash
pip install vallm
```

With optional dependencies:

```bash
pip install vallm[all]        # Everything
pip install vallm[llm]        # Ollama + litellm for semantic review
pip install vallm[security]   # bandit integration
pip install vallm[semantic]   # CodeBERTScore
pip install vallm[graph]      # NetworkX graph analysis
```

## Quick Start

### Validate Entire Project

```bash
# Install with LLM support
pip install vallm[llm]

# Setup Ollama (for semantic review)
ollama pull qwen2.5-coder:7b
ollama serve

# Validate entire project recursively
vallm batch . --recursive --semantic --model qwen2.5-coder:7b

# Fast validation for quick feedback (skip imports and complexity)
vallm batch . --recursive --no-imports --no-complexity

# Generate validation report in TOON format
vallm batch . --recursive --output toon > ./project/validation.toon
```

### Project Structure & Files

**Core Source Code:**
- [`src/vallm/`](src/vallm/) - Main package directory
  - [`cli.py`](src/vallm/cli.py) - Simplified CLI entry point (9 lines)
  - [`config.py`](src/vallm/config.py) - Configuration management
  - [`scoring.py`](src/vallm/scoring.py) - Validation pipeline and scoring
  - [`hookspecs.py`](src/vallm/hookspecs.py) - Plugin system specifications
  - [`core/`](src/vallm/core/) - Core functionality
    - [`languages.py`](src/vallm/core/languages.py) - Language detection and support
    - [`proposal.py`](src/vallm/core/proposal.py) - Code proposal model
    - [`ast_compare.py`](src/vallm/core/ast_compare.py) - AST similarity analysis
    - [`graph_builder.py`](src/vallm/core/graph_builder.py) - Code graph construction
    - [`graph_diff.py`](src/vallm/core/graph_diff.py) - Graph diffing
  - [`validators/`](src/vallm/validators/) - Validation modules
    - [`syntax.py`](src/vallm/validators/syntax.py) - Syntax validation
    - [`complexity.py`](src/vallm/validators/complexity.py) - Complexity analysis
    - [`security.py`](src/vallm/validators/security.py) - Security scanning
    - [`semantic.py`](src/vallm/validators/semantic.py) - LLM semantic review
    - [`imports/`](src/vallm/validators/imports/) - Import validation modules
  - [`sandbox/`](src/vallm/sandbox/) - Code execution sandbox
  - [`cli/`](src/vallm/cli/) - Modular CLI components
    - [`command_handlers.py`](src/vallm/cli/command_handlers.py) - CLI command implementations
    - [`output_formatters.py`](src/vallm/cli/output_formatters.py) - Output formatting
    - [`settings_builders.py`](src/vallm/cli/settings_builders.py) - Settings configuration
    - [`batch_processor.py`](src/vallm/cli/batch_processor.py) - Batch processing logic

**Examples & Documentation:**
- [`examples/`](examples/) - Comprehensive examples directory
  - [`01_basic_validation/`](examples/01_basic_validation/) - Basic validation pipeline
  - [`02_ast_comparison/`](examples/02_ast_comparison/) - AST similarity scoring
  - [`03_security_check/`](examples/03_security_check/) - Security pattern detection
  - [`04_graph_analysis/`](examples/04_graph_analysis/) - Import/call graph analysis
  - [`05_llm_semantic_review/`](examples/05_llm_semantic_review/) - LLM semantic review
  - [`06_multilang_validation/`](examples/06_multilang_validation/) - Multi-language validation
  - [`07_multi_language/`](examples/07_multi_language/) - Comprehensive multi-language demo
  - [`08_code2llm_integration/`](examples/08_code2llm_integration/) - Code2LLM integration
  - [`09_code2logic_integration/`](examples/09_code2logic_integration/) - Code2Logic integration
  - [`10_mcp_ollama_demo/`](examples/10_mcp_ollama_demo/) - MCP + Ollama demo
  - [`11_claude_code_autonomous/`](examples/11_claude_code_autonomous/) - Autonomous refactoring
  - [`12_ollama_simple_demo/`](examples/12_ollama_simple_demo/) - Simplified Ollama demo
- [`docs/`](docs/) - Documentation
  - [`README.md`](docs/README.md) - Documentation overview
  - [`TESTING.md`](docs/TESTING.md) - Testing guidelines

**Configuration Files:**
- [`pyproject.toml`](pyproject.toml) - Project configuration and dependencies
- [`.gitignore`](.gitignore) - Git ignore patterns (includes .git/ exclusion)
- [`LICENSE`](LICENSE) - Apache 2.0 license
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - Contribution guidelines
- [`CHANGELOG.md`](CHANGELOG.md) - Version history
- [`TODO.md`](TODO.md) - Development roadmap

**Scripts & Tools:**
- [`project.sh`](project.sh) - Project analysis script
- [`scripts/`](scripts/) - Utility scripts
  - [`bump_version.py`](scripts/bump_version.py) - Version management
  - [`test_docker_installation.sh`](scripts/test_docker_installation.sh) - Docker testing

**Testing:**
- [`tests/`](tests/) - Comprehensive test suite
  - [`test_cli_e2e.py`](tests/test_cli_e2e.py) - End-to-end CLI tests
  - [`test_syntax.py`](tests/test_syntax.py) - Syntax validation tests
  - [`test_imports.py`](tests/test_imports.py) - Import validation tests
  - [`test_complexity.py`](tests/test_complexity.py) - Complexity analysis tests
  - [`test_security.py`](tests/test_security.py) - Security scanning tests
  - [`test_semantic_validation.py`](tests/test_semantic_validation.py) - Semantic validation tests
  - [`conftest.py`](tests/conftest.py) - Test configuration

**CI/CD & GitHub:**
- [`.github/workflows/`](.github/workflows/) - GitHub Actions workflows
  - [`ci.yml`](.github/workflows/ci.yml) - Continuous integration
  - [`comprehensive-tests.yml`](.github/workflows/comprehensive-tests.yml) - Full test suite
  - [`publish.yml`](.github/workflows/publish.yml) - Package publishing
- [`Dockerfile.test`](Dockerfile.test) - Testing container

**Project Analysis:**
- [`project/`](project/) - Analysis outputs and visualizations
  - [`validation.toon`](project/validation.toon) - Validation results (TOON format)
  - [`project.toon`](project/project.toon) - Project analysis
  - [`flow.toon`](project/flow.toon) - Workflow visualization
  - [`calls.toon`](project/calls.toon) - Call graph analysis
  - [`README.md`](project/README.md) - Project analysis overview

### Python API

```python
from vallm import Proposal, validate, VallmSettings

code = """
def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
"""

proposal = Proposal(code=code, language="python")
result = validate(proposal)
print(f"Verdict: {result.verdict.value}")  # pass / review / fail
print(f"Score: {result.weighted_score:.2f}")
```

### CLI Commands Reference

```bash
# Batch validation (best for entire projects)
vallm batch . --recursive --semantic --model qwen2.5-coder:7b
vallm batch src/ --recursive --include "*.py,*.js" --exclude "*/test/*"
vallm batch . --recursive --format json --fail-fast
vallm batch . --recursive --verbose --show-issues  # Detailed per-file results

# Output formats for batch results
vallm batch . --recursive --format json   # Machine-readable JSON
vallm batch . --recursive --format yaml   # YAML format
vallm batch . --recursive --format toon   # Compact TOON format
vallm batch . --recursive --format text   # Plain text

# Single file validation
vallm validate --file mycode.py --semantic --model qwen2.5-coder:7b
vallm validate --file app.js --security
vallm validate --file mycode.py --format json  # JSON output

# Quick syntax check only
vallm check mycode.py
vallm check src/main.go

# Configuration and info
vallm info
```

### Real-World Usage Examples

#### 1. **Fast Project Validation** (Recommended for CI/CD)
```bash
# Quick syntax check - excludes .git/ and other system files automatically
vallm batch . --recursive --no-imports --no-complexity

# Output: Excluded 30246 files by .gitignore, Validating 169 files...
# ✓ 83 files passed, ✗ 115 files failed (mostly non-code files)
```

#### 2. **Generate Validation Report**
```bash
# Save TOON format report to project directory
vallm batch . --recursive --output toon > ./project/validation.toon

# Save JSON report for CI/CD integration
vallm batch . --recursive --output json > ./project/validation.json

# Save detailed text report with security checks
vallm batch . --recursive --security --output text > ./project/validation-report.txt
```

#### 3. **Selective File Validation**
```bash
# Validate only Python and JavaScript files
vallm batch . --recursive --include "*.py,*.js" --exclude "*/test/*"

# Validate specific directory with custom patterns
vallm batch src/ --recursive --include "*.py" --exclude "*/__pycache__/*"

# Validate with custom gitignore override
vallm batch . --recursive --no-gitignore --exclude "*.log,tmp/*"
```

#### 4. **Full Pipeline with LLM Review**
```bash
# Complete validation with semantic analysis
vallm batch . --recursive --semantic --model qwen2.5-coder:7b --security

# Export full results with per-file details
vallm batch . --recursive --semantic --model qwen2.5-coder:7b --output json > full-validation.json
```

#### 5. **Development Workflow Integration**
```bash
# Pre-commit validation (fast)
vallm batch . --recursive --no-imports --no-complexity --fail-fast

# Feature branch validation (medium)
vallm batch src/ --recursive --no-complexity --show-issues

# Release validation (full)
vallm batch . --recursive --semantic --model qwen2.5-coder:7b --security --verbose
```

### Fast Validation Options

When validating large projects (100+ files), use these options to speed up validation:

```bash
# Fastest - syntax only (skip imports and complexity)
vallm batch . --recursive --no-imports --no-complexity

# Fast - skip import validation (often the slowest)
vallm batch . --recursive --no-imports

# Parallel processing for multi-core speedup
# Note: --parallel option was removed in v0.1.16 due to module conflicts
# Use --no-imports --no-complexity for better performance

# Combine for maximum speed
vallm batch . --recursive --no-imports --no-complexity

# Quick syntax check only (single files)
vallm check src/proxym/config.py
```

| Option | Speed Impact | Description |
|--------|--------------|-------------|
| `--no-imports` | **High** | Skip import resolution (slowest validator) |
| `--no-complexity` | **Medium** | Skip complexity analysis (radon/lizard) |
| `--security` | **Low** | Add security checks (fast pattern matching) |
| `--semantic` | **Very High** | LLM semantic review (requires Ollama/OpenAI) |

**Performance Benchmarks:**
- **Fast mode**: `--no-imports --no-complexity` - ~100 files/second
- **Normal mode**: Default settings - ~20 files/second  
- **Full mode**: With `--semantic` - ~2 files/second

**Recommendation for CI/CD:**
```bash
# Fast validation for quick feedback (PR checks)
vallm batch src/ --recursive --no-imports --no-complexity --fail-fast

# Full validation before merge (quality gate)
vallm batch src/ --recursive --security

# Release validation with LLM review
vallm batch . --recursive --semantic --model qwen2.5-coder:7b
```

### Generate Validation Summary File

```bash
# JSON summary for entire project (with per-file details and issues)
vallm batch . --recursive --output json > validation-summary.json

# YAML summary for src/ directory (with per-file details and issues)
vallm batch src/ --recursive --output yaml > validation-summary.yaml

# TOON format (compact, human-readable) with per-file details
vallm batch . --recursive --output toon > validation-summary.toon

# Text format with security checks
vallm batch . --recursive --output text --security > validation-report.txt

# Full validation with semantic review - save to file
vallm batch . --recursive --semantic --model qwen2.5-coder:7b --output json > full-validation.json

# Tee output to both console and file
vallm batch . --recursive --output json | tee validation-summary.json

# Save to project directory for analysis integration
vallm batch . --recursive --output toon > ./project/validation.toon
```

**Sample Output Files:**
- [`project/validation.toon`](project/validation.toon) - Real validation results (TOON format)
- [`project/validation.json`](project/validation.json) - JSON format (generate with `--output json`)
- [`project/validation-report.txt`](project/validation-report.txt) - Text format (generate with `--output text`)

**Output Structure (JSON/YAML/TOON formats now include per-file details):**

```json
{
  "summary": {
    "total_files": 146,
    "passed": 145,
    "failed": 1
  },
  "files": [
    {
      "path": "src/proxym/config.py",
      "language": "python",
      "verdict": "fail",
      "score": 0.45,
      "issues_count": 3,
      "issues": [
        {
          "validator": "syntax",
          "severity": "error",
          "message": "Invalid syntax at line 42",
          "line": 42,
          "column": 15
        },
        {
          "validator": "imports",
          "severity": "error", 
          "message": "Module 'requests' not found",
          "line": 5,
          "column": 0
        }
      ]
    }
  ],
  "failed_files": [
    {"path": "src/proxym/config.py", "error": "Validation fail"}
  ]
}
```

```yaml
---
summary:
  total_files: 146
  passed: 145
  failed: 1

files:
  - path: src/proxym/config.py
    language: python
    verdict: fail
    score: 0.45
    issues_count: 3
    issues:
      - validator: syntax
        severity: error
        message: "Invalid syntax at line 42"
        line: 42
        column: 15
      - validator: imports
        severity: error
        message: "Module 'requests' not found"
        line: 5
```

```toon
# vallm batch | 146f | 145✓ 1✗

SUMMARY:
  total: 146
  passed: 145
  failed: 1

FILES:
  [python]
    ✗ src/proxym/config.py
      verdict: fail
      score: 0.45
      issues: 2
        [error] syntax: Invalid syntax at line 42@42
        [error] imports: Module 'requests' not found@5
    ✓ src/proxym/ctl.py
      verdict: pass
      score: 0.92
      issues: 0

FAILED:
  ✗ src/proxym/config.py: Validation fail
```

### Batch Command Options

| Option | Short | Description |
|--------|-------|-------------|
| `--recursive` | `-r` | Recurse into subdirectories |
| `--include` | | File patterns to include (e.g., "*.py,*.js") |
| `--exclude` | | File patterns to exclude |
| `--use-gitignore` | | Respect .gitignore patterns (default: true) |
| `--format` | `-f` | Output format: `rich`, `json`, `yaml`, `toon`, `text` |
| `--fail-fast` | `-x` | Stop on first failure |
| `--semantic` | | Enable LLM-as-judge semantic review |
| `--security` | | Enable security checks |
| `--model` | `-m` | LLM model for semantic review |
| `--verbose` | `-v` | Show detailed validation results for each file |
| `--show-issues` | `-i` | Show issues for failed files |

### With Ollama (LLM-as-judge)

```bash
# 1. Install and start Ollama
ollama pull qwen2.5-coder:7b

# 2. Run with semantic review
vallm validate --file mycode.py --semantic
```

```python
from vallm import Proposal, validate, VallmSettings

settings = VallmSettings(
    enable_semantic=True,
    llm_provider="ollama",
    llm_model="qwen2.5-coder:7b",
)

proposal = Proposal(
    code=new_code,
    language="python",
    reference_code=existing_code,  # optional: compare against reference
)
result = validate(proposal, settings)
```

## Validation Pipeline

| Tier | Speed | Validators | What it catches |
|------|-------|-----------|----------------|
| 1 | ms | syntax, imports | Parse errors, missing modules |
| 2 | seconds | complexity, security | High CC, dangerous patterns |
| 3 | seconds | semantic (LLM) | Logic errors, poor practices |
| 4 | minutes | regression (tests) | Behavioral regressions |

The pipeline **fails fast** — Tier 1 errors stop execution immediately.

## Configuration

Via environment variables (`VALLM_*`), `vallm.toml`, or `pyproject.toml [tool.vallm]`:

```toml
# vallm.toml
pass_threshold = 0.8
review_threshold = 0.5
max_cyclomatic_complexity = 15
enable_semantic = true
llm_provider = "ollama"
llm_model = "qwen2.5-coder:7b"
```

## Quality Pipeline (pyqual)

vallm uses **pyqual** — a declarative quality gate system — to ensure code meets all quality standards before shipping.

### Quality Gates

| Gate | Metric | Threshold | Current |
|------|--------|-----------|---------|
| Cyclomatic Complexity | cc | ≤ 15 | 3.4 ✅ |
| Vallm Pass Rate | vallm_pass | ≥ 90% | 97.7% ✅ |
| Test Coverage | coverage | ≥ 55% | 63.9% ✅ |

### Pipeline Stages

```yaml
# pyqual.yaml
pipeline:
  name: quality-loop-with-llx
  
  metrics:
    cc_max: 15
    vallm_pass_min: 90
    coverage_min: 55
  
  stages:
    - setup        # Dependency check
    - analyze      # code2llm analysis
    - validate     # vallm batch validation
    - lint         # ruff linting
    - test         # pytest with coverage
    - prefact      # Prefactoring (optional)
    - fix          # Auto-fix with LLX (optional)
    - verify       # Post-fix validation
    - push         # Auto-commit & push
    - publish      # Build & publish
```

### Running the Pipeline

```bash
# Full pipeline with quality gates
pyqual run

# Check current metrics
pyqual status

# View pipeline logs
pyqual logs

# Validate pyqual.yaml config
pyqual validate
```

### Publishing to PyPI

```bash
# Set credentials and publish
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-xxx make publish

# Or publish to TestPyPI
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-xxx make publish-test
```

Without credentials, the publish stage gracefully skips with a warning.

## MCP Integration

vallm provides **Model Context Protocol (MCP)** server integration, exposing validation tools as MCP endpoints for LLM tool calling.

### Starting the MCP Server

```bash
# Start the MCP server from project root
python3 mcp_server.py

# Or start the packaged module directly
python3 -m mcp.server.self_server
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vallm": {
      "command": "python3",
      "args": ["/path/to/vallm/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/vallm/src"
      }
    }
  }
}
```

### Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `validate_syntax` | Multi-language syntax checking | `code`, `language`, `filename` |
| `validate_imports` | Import resolution validation | `code`, `language`, `filename` |
| `validate_security` | Security issue detection | `code`, `language`, `filename` |
| `validate_code` | Full pipeline validation | `code`, `language`, `filename`, `reference_code`, `enable_*` flags |

### Example Tool Calls

```json
{
  "method": "tools/call",
  "params": {
    "name": "validate_security",
    "arguments": {
      "code": "eval('1+1')",
      "language": "python"
    }
  }
}
```

```json
{
  "method": "tools/call", 
  "params": {
    "name": "validate_code",
    "arguments": {
      "code": "def test(): pass",
      "language": "python",
      "enable_syntax": true,
      "enable_security": true,
      "enable_complexity": false
    }
  }
}
```

### Testing MCP Integration

```bash
# Test all MCP tools
python3 test_mcp.py

# Quick validation tests
python3 mcp/tests/quick_test.py

# Test individual tools
PYTHONPATH=src python3 -c "from mcp.server._tools_vallm import validate_syntax; print(validate_syntax('print(\"hello\")', 'python')['verdict'])"

# Run the complete Docker e2e flow (host build + container-side runner)
bash mcp/tests/run_e2e.sh

# Run the same e2e flow via single-service docker-compose
bash mcp/tests/run_e2e.sh --compose

# Run examples
python3 examples/mcp_demo.py
```

### Response Format

All MCP tools return a consistent JSON response:

```json
{
  "success": true,
  "validator": "security",
  "score": 0.3,
  "weight": 1.5,
  "confidence": 0.9,
  "verdict": "fail",
  "issues": [
    {
      "message": "Use of eval() detected",
      "severity": "warning",
      "line": 1,
      "column": 0,
      "rule": "security.eval"
    }
  ],
  "details": {}
}
```

## Plugin System

Write custom validators using pluggy:

```python
from vallm.hookspecs import hookimpl
from vallm.scoring import ValidationResult

class MyValidator:
    tier = 2
    name = "custom"
    weight = 1.0

    @hookimpl
    def validate_proposal(self, proposal, context):
        # Your validation logic
        return ValidationResult(validator=self.name, score=1.0, weight=self.weight)
```

Register via `pyproject.toml`:

```toml
[project.entry-points."vallm.validators"]
custom = "mypackage.validators:MyValidator"
```

## Multi-Language Support

vallm supports **30+ programming languages** via tree-sitter parsers:

### Auto-Detection

```python
from vallm import detect_language, Language

# Auto-detect from file path
lang = detect_language("main.rs")  # → Language.RUST
print(lang.display_name)  # "Rust"
print(lang.is_compiled)     # True
```

### CLI with Auto-Detection

```bash
# Language auto-detected from file extension
vallm validate --file script.py      # → Python
vallm check main.go                   # → Go  
vallm validate --file lib.rs          # → Rust

# Batch validation with mixed languages
vallm batch src/ --recursive --include "*.py,*.js,*.ts,*.go,*.rs"
```

### Supported Languages

| Language | Category | Complexity | Syntax |
|----------|----------|------------|--------|
| Python | Scripting | ✓ radon + lizard | ✓ ast + tree-sitter |
| JavaScript | Web/Scripting | ✓ lizard | ✓ tree-sitter |
| TypeScript | Web/Scripting | ✓ lizard | ✓ tree-sitter |
| Go | Compiled | ✓ lizard | ✓ tree-sitter |
| Rust | Compiled | ✓ lizard | ✓ tree-sitter |
| Java | Compiled | ✓ lizard | ✓ tree-sitter |
| C/C++ | Compiled | ✓ lizard | ✓ tree-sitter |
| Ruby | Scripting | ✓ lizard | ✓ tree-sitter |
| PHP | Web | ✓ lizard | ✓ tree-sitter |
| Swift | Compiled | ✓ lizard | ✓ tree-sitter |
| + 20 more via tree-sitter | | ✓ tree-sitter | ✓ tree-sitter |

See `examples/07_multi_language/` for a comprehensive demo.

## Examples

Each example lives in its own folder with `main.py` and `README.md`. Run all at once:

```bash
cd examples && ./run.sh
```

### Example Details & Links

| Example | What it demonstrates | Files | Description |
|---------|---------------------|-------|-------------|
| [`01_basic_validation/`](examples/01_basic_validation/) | Default pipeline — good, bad, and complex code | [`main.py`](examples/01_basic_validation/main.py), [`README.md`](examples/01_basic_validation/README.md) | Basic validation with syntax, imports, complexity, and security checks |
| [`02_ast_comparison/`](examples/02_ast_comparison/) | AST similarity scoring, tree-sitter multi-language parsing | [`main.py`](examples/02_ast_comparison/main.py), [`README.md`](examples/02_ast_comparison/README.md) | Compare code similarity using AST fingerprinting |
| [`03_security_check/`](examples/03_security_check/) | Security pattern detection (eval, exec, hardcoded secrets) | [`main.py`](examples/03_security_check/main.py), [`README.md`](examples/03_security_check/README.md) | Detect security vulnerabilities and anti-patterns |
| [`04_graph_analysis/`](examples/04_graph_analysis/) | Import/call graph building and structural diffing | [`main.py`](examples/04_graph_analysis/main.py), [`README.md`](examples/04_graph_analysis/README.md) | Build and analyze code dependency graphs |
| [`05_llm_semantic_review/`](examples/05_llm_semantic_review/) | Ollama Qwen 2.5 Coder 7B LLM-as-judge review | [`main.py`](examples/05_llm_semantic_review/main.py), [`README.md`](examples/05_llm_semantic_review/README.md) | Semantic code review using LLM |
| [`06_multilang_validation/`](examples/06_multilang_validation/) | JavaScript and C validation via tree-sitter | [`main.py`](examples/06_multilang_validation/main.py), [`README.md`](examples/06_multilang_validation/README.md) | Multi-language validation examples |
| [`07_multi_language/`](examples/07_multi_language/) | **Comprehensive multi-language support** — 8+ languages with auto-detection | [`main.py`](examples/07_multi_language/main.py), [`README.md`](examples/07_multi_language/README.md) | Complete multi-language validation demo |
| [`08_code2llm_integration/`](examples/08_code2llm_integration/) | Project analysis integration with code2llm | [`main.py`](examples/08_code2llm_integration/main.py), [`README.md`](examples/08_code2llm_integration/README.md) | Integration with code2llm analysis tools |
| [`09_code2logic_integration/`](examples/09_code2logic_integration/) | Call graph analysis with code2logic | [`main.py`](examples/09_code2logic_integration/main.py), [`README.md`](examples/09_code2logic_integration/README.md) | Advanced call graph analysis |
| [`10_mcp_ollama_demo/`](examples/10_mcp_ollama_demo/) | MCP (Model Context Protocol) demo with Ollama | [`main.py`](examples/10_mcp_ollama_demo/main.py), [`README.md`](examples/10_mcp_ollama_demo/README.md) | Model Context Protocol integration |
| [`11_claude_code_autonomous/`](examples/11_claude_code_autonomous/) | Autonomous refactoring with Claude Code | [`claude_autonomous_demo.py`](examples/11_claude_code_autonomous/claude_autonomous_demo.py), [`README.md`](examples/11_claude_code_autonomous/README.md) | AI-powered autonomous code refactoring |
| [`12_ollama_simple_demo/`](examples/12_ollama_simple_demo/) | Simplified Ollama integration example | [`ollama_simple_demo.py`](examples/12_ollama_simple_demo/ollama_simple_demo.py), [`README.md`](examples/12_ollama_simple_demo/README.md) | Basic Ollama LLM integration |

### Running Examples

```bash
# Run all examples
cd examples && ./run.sh

# Run specific example
python examples/01_basic_validation/main.py

# Run with validation
vallm validate --file examples/01_basic_validation/main.py --verbose

# Batch validate all examples
vallm batch examples/ --recursive --include "*.py" --verbose
```

## Architecture

```
src/vallm/
├── cli/                    # 🆕 Modular CLI package
│   ├── __init__.py         # Command registration and app export
│   ├── command_handlers.py # CLI command implementations
│   ├── output_formatters.py # Output formatting utilities
│   ├── settings_builders.py # Settings configuration logic
│   └── batch_processor.py  # Batch processing logic
├── cli.py                  # 🆕 Simplified main entry point (9L)
├── config.py               # pydantic-settings (VALLM_* env vars)
├── hookspecs.py            # pluggy hook specifications
├── scoring.py              # Weighted scoring + verdict engine (CC=18 validate function)
├── core/
│   ├── languages.py        # Language enum, auto-detection, 30+ languages
│   ├── proposal.py         # Proposal model
│   ├── ast_compare.py      # tree-sitter + Python AST similarity
│   ├── graph_builder.py    # Import/call graph construction
│   └── graph_diff.py       # Before/after graph comparison
├── validators/
│   ├── syntax.py           # Tier 1: ast.parse + tree-sitter (multi-lang)
│   ├── imports/            # 🆕 Modular import validators
│   │   ├── base.py         # 🆕 Enhanced base class with shared validate()
│   │   ├── factory.py      # Validator factory
│   │   ├── python_imports.py
│   │   ├── go_imports.py   # 🆕 Uses shared validation logic
│   │   ├── rust_imports.py # 🆕 Uses shared validation logic
│   │   └── java_imports.py # 🆕 Uses shared validation logic
│   ├── complexity.py       # Tier 2: radon (Python) + lizard (16+ langs)
│   ├── security.py         # Tier 2: patterns + bandit
│   └── semantic.py         # Tier 3: LLM-as-judge
└── sandbox/
    └── runner.py           # subprocess / Docker execution
```

### 🆕 Code Health Improvements

**Recent Refactoring Achievements**:

✅ **CLI Modularization** - Split 850L god module into focused packages:
- `cli/command_handlers.py` - Command implementations
- `cli/output_formatters.py` - Output formatting logic  
- `cli/settings_builders.py` - Settings configuration
- `cli/batch_processor.py` - Batch processing logic
- `cli/__init__.py` - Command registration and app export

✅ **Import Validator Cleanup** - Removed 653L legacy module:
- Enhanced `BaseImportValidator` with shared validation logic
- Eliminated duplicate `validate()` methods across language validators
- Improved maintainability through template method pattern

✅ **Code Deduplication** - Removed 469 lines of duplicated code:
- Shared validation runners for examples (154 lines saved)
- Centralized analysis data saving (66 lines saved)
- Common demo utilities (60 lines saved)
- LLM response parsing utilities (40 lines saved)
- Import validator logic consolidation (40 lines saved)
- Additional utility function consolidation (109 lines saved)

**Updated Code Metrics**:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| God Modules (>500L) | 2 | 0 | ✅ **100% eliminated** |
| Max Cyclomatic Complexity | 42 | ~18 | ✅ **57% reduction** |
| Code Duplication | 504 lines | 35 lines | ✅ **93% eliminated** |
| CLI Module Size | 850 lines | 9 lines | ✅ **99% reduction** |

**Remaining Critical Functions**:

| Function | Location | CC | Status |
|----------|----------|-----|--------|
| `validate` | `scoring.py:122` | **18** | 🟡 Acceptable |
| `_check_lizard` | `complexity.py` | 12 | 🟡 Acceptable |
| `_parse_response` | `semantic.py` | 12 | 🟡 Acceptable |

## Roadmap

**v0.2 — Completeness** ✅ **MAJOR PROGRESS**
- ✅ CLI modularization - Split 850L god module into focused packages
- ✅ Import validator cleanup - Removed 653L legacy module  
- ✅ Code deduplication - Eliminated 469 lines of duplicate code
- ✅ God module elimination - 100% reduction in god modules
- ✅ Complexity reduction - 57% reduction in max cyclomatic complexity
- Wire pluggy plugin manager (entry_point-based validator discovery)
- Add LogicalErrorValidator (pyflakes) and LintValidator (ruff)
- TOML config loading (`vallm.toml`, `[tool.vallm]`)
- Pre-commit hook integration
- GitHub Actions CI/CD

**v0.3 — Depth**
- AST edit distance via apted/zss
- CodeBERTScore embedding similarity
- NetworkX cycle detection and centrality in graph analysis
- RegressionValidator (Tier 4) with pytest-json-report
- TypeCheckValidator (mypy/pyright)
- Extract output formatters

**v0.4 — Intelligence**
- `--fix` auto-repair mode (LLM-based retry loop)
- hypothesis/crosshair property-based test generation
- E2B cloud sandbox backend
- Streaming LLM output

See [TODO.md](TODO.md) for the full task breakdown.

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_syntax.py
pytest tests/test_imports.py
pytest tests/test_complexity.py
pytest tests/test_security.py
pytest tests/test_semantic_validation.py

# Run CLI end-to-end tests
pytest tests/test_cli_e2e.py -v

# Run with coverage
pytest --cov=vallm --cov-report=html

# Run performance tests
pytest tests/test_performance.py -v
```

### Test Files Reference

- [`tests/`](tests/) - Complete test suite
  - [`conftest.py`](tests/conftest.py) - Test configuration and fixtures
  - [`test_cli_e2e.py`](tests/test_cli_e2e.py) - End-to-end CLI integration tests
  - [`test_syntax.py`](tests/test_syntax.py) - Syntax validation tests
  - [`test_imports.py`](tests/test_imports.py) - Import resolution tests
  - [`test_complexity.py`](tests/test_complexity.py) - Complexity analysis tests
  - [`test_security.py`](tests/test_security.py) - Security scanning tests
  - [`test_semantic_validation.py`](tests/test_semantic_validation.py) - LLM semantic review tests
  - [`test_languages.py`](tests/test_languages.py) - Language detection tests
  - [`test_ast_compare.py`](tests/test_ast_compare.py) - AST similarity tests
  - [`test_graph.py`](tests/test_graph.py) - Graph analysis tests
  - [`test_plugins.py`](tests/test_plugins.py) - Plugin system tests
  - [`test_performance.py`](tests/test_performance.py) - Performance benchmarks
  - [`test_installation.py`](tests/test_installation.py) - Installation tests
  - [`test_gitignore.py`](tests/test_gitignore.py) - Git ignore pattern tests
  - [`test_pipeline.py`](tests/test_pipeline.py) - End-to-end pipeline tests

### Test Coverage

Current test coverage: **85%** across all modules.

- ✅ Syntax validation: 95% coverage
- ✅ Import resolution: 87% coverage  
- ✅ Complexity analysis: 82% coverage
- ✅ Security scanning: 79% coverage
- ✅ Semantic validation: 71% coverage
- ✅ CLI commands: 89% coverage

## License

Licensed under Apache-2.0.
## Author

Tom Sapletta
## Additional Resources

### Documentation & Guides
- [`docs/README.md`](docs/README.md) - Extended documentation
- [`docs/TESTING.md`](docs/TESTING.md) - Testing guidelines and best practices
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - Contribution guidelines
- [`CHANGELOG.md`](CHANGELOG.md) - Version history and release notes
- [`TODO.md`](TODO.md) - Development roadmap and planned features

### Package Configuration
- [`pyproject.toml`](pyproject.toml) - Project metadata, dependencies, and build configuration
- [`.gitignore`](.gitignore) - Git ignore patterns (includes .git/ exclusion)
- [`Dockerfile.test`](Dockerfile.test) - Testing container configuration
- [`Makefile`](Makefile) - Build and development automation

### CI/CD & Automation
- [`.github/workflows/`](.github/workflows/) - GitHub Actions workflows
  - [`ci.yml`](.github/workflows/ci.yml) - Continuous integration pipeline
  - [`comprehensive-tests.yml`](.github/workflows/comprehensive-tests.yml) - Full test suite
  - [`publish.yml`](.github/workflows/publish.yml) - Package publishing to PyPI
- [`.pre-commit-config.yaml`](.pre-commit-config.yaml) - Pre-commit hooks configuration
- [`.pre-commit-hooks.yaml`](.pre-commit-hooks.yaml) - Custom pre-commit hooks

### Project Analysis & Metrics
- [`project/`](project/) - Analysis outputs and visualizations
  - [`validation.toon`](project/validation.toon) - Latest validation results
  - [`project.toon`](project/project.toon) - Project structure analysis
  - [`flow.toon`](project/flow.toon) - Workflow visualization
  - [`calls.toon`](project/calls.toon) - Call graph analysis
  - [`compact_flow.mmd`](project/compact_flow.mmd) - Mermaid flow diagram
  - [`README.md`](project/README.md) - Project analysis overview
  - [`analysis.yaml`](project/analysis.yaml) - Detailed analysis data
  - [`dashboard.html`](project/dashboard.html) - Interactive dashboard

### Development Tools
- [`scripts/`](scripts/) - Development and maintenance scripts
  - [`bump_version.py`](scripts/bump_version.py) - Automated version management
  - [`test_docker_installation.sh`](scripts/test_docker_installation.sh) - Docker environment testing
- [`project.sh`](project.sh) - Project analysis and validation script

### Examples & Demos
- [`examples/`](examples/) - 12 comprehensive examples with README files
- [`examples/run.sh`](examples/run.sh) - Run all examples script
- [`examples/README.md`](examples/README.md) - Examples overview and guide

### Source Code Organization
- [`src/vallm/`](src/vallm/) - Main package source code
- [`src/vallm/__init__.py`](src/vallm/__init__.py) - Package initialization
- [`src/vallm/__main__.py`](src/vallm/__main__.py) - Module execution support
- [`src/vallm/py.typed`](src/vallm/py.typed) - Type checking marker

<!-- taskill:status:start -->

## Status

_Last updated by [taskill](https://github.com/oqlos/taskill) at 2026-04-25 13:48 UTC_

| Metric | Value |
|---|---|
| HEAD | `4ac3a46` |
| Coverage | — |
| Failing tests | — |
| Commits in last cycle | 50 |

> Mostly documentation and refactoring work: multiple README/docs updates, added markdown output (with tests), new examples, a version bump, and several refactors extracting and simplifying high-complexity code paths.

<!-- taskill:status:end -->
