# vallm

**A complete toolkit for validating LLM-generated code.**

[![PyPI](https://img.shields.io/pypi/v/vallm)](https://pypi.org/project/vallm/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vallm)](https://pypi.org/project/vallm/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/semcod/vallm/actions)
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

vallm validates code proposals through a **four-tier pipeline** — from millisecond syntax checks to LLM-as-judge semantic review — before a single line ships.

## Features

- **Multi-language AST parsing** via tree-sitter (165+ languages)
- **Syntax validation** with ast.parse and tree-sitter error detection
- **Import resolution** checking for Python
- **Complexity metrics** via radon (Python) and lizard (16 languages)
- **Security scanning** with pattern matching and optional bandit integration
- **LLM-as-judge** semantic review via Ollama, litellm, or direct HTTP
- **Code graph analysis** — import/call graph diffing for structural regression detection
- **AST similarity scoring** with normalized fingerprinting
- **Pluggy-based plugin system** for custom validators
- **Rich CLI** with JSON/text output formats

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

### CLI

```bash
# Validate a file
vallm validate --file mycode.py

# Quick syntax check
vallm check mycode.py

# With LLM semantic review (requires Ollama)
vallm validate --file mycode.py --semantic --model qwen2.5-coder:7b

# JSON output
vallm validate --file mycode.py --format json

# Show config and available validators
vallm info
```

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

## Examples

See the `examples/` directory:

- `01_basic_validation.py` — Default pipeline with good, bad, and complex code
- `02_ast_comparison.py` — AST similarity and structural diff
- `03_security_check.py` — Security pattern detection
- `04_graph_analysis.py` — Import/call graph diffing
- `05_llm_semantic_review.py` — Ollama LLM-as-judge review
- `06_multilang_validation.py` — JavaScript and C validation

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Author

Created by **Tom Sapletta** - [tom@sapletta.com](mailto:tom@sapletta.com)
