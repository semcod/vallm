# Contributing to vallm

Thank you for your interest in contributing to vallm! This document provides guidelines and information for contributors.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/semcod/vallm
cd vallm

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

## Development Guidelines

### Quality Pipeline

We use **pyqual** — a declarative quality gate system — to ensure all code meets quality standards before merging:

```bash
# Run full quality pipeline (includes tests, linting, coverage)
pyqual run

# Check current metrics without running pipeline
pyqual status

# View pipeline logs
pyqual logs
```

**Quality Gates:**
| Gate | Threshold | Current |
|------|-----------|---------|
| Cyclomatic Complexity | ≤ 15 | 3.4 ✅ |
| Vallm Pass Rate | ≥ 90% | 97.7% ✅ |
| Test Coverage | ≥ 55% | 63.9% ✅ |

All gates must pass before code can be pushed/published.

### Code Quality Standards

We use the following tools to maintain code quality:

| Tool | Purpose | Command |
|------|---------|---------|
| ruff | Linting and formatting | `ruff check .` / `ruff format .` |
| mypy | Type checking | `mypy src/vallm` |
| pytest | Testing | `pytest` |
| bandit | Security scanning | `bandit -r src/vallm` |

### Pre-commit Hooks

Install pre-commit hooks to catch issues before committing:

```bash
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/vallm --cov-report=html

# Run specific test file
pytest tests/test_syntax.py

# Run with verbose output
pytest -v
```

## Project Structure

```
src/vallm/
├── cli.py              # CLI commands (needs refactoring - see TODO.md)
├── config.py           # Configuration management
├── scoring.py          # Validation pipeline scoring
├── core/               # Core utilities
│   ├── ast_compare.py
│   ├── gitignore.py
│   ├── graph_builder.py
│   ├── graph_diff.py
│   ├── languages.py
│   └── proposal.py
├── validators/         # Validation plugins
│   ├── base.py
│   ├── complexity.py
│   ├── imports.py      # God module - needs splitting
│   ├── security.py
│   ├── semantic.py
│   └── syntax.py
└── sandbox/            # Code execution sandbox
    └── runner.py
```

## Code Health & Refactoring

We actively monitor code complexity. Before contributing, check the current metrics:

```bash
# Generate code health analysis
code2llm ./ -f toon -o ./project

# View critical issues
cat ./project/analysis.toon | head -50
```

### Refactoring Priorities

See [TODO.md](TODO.md) for current refactoring priorities. Key areas:

1. **High Priority**: Split `cli.batch` (CC=42) and `scoring.validate` (CC=18)
2. **God Modules**: Modularize `validators/imports.py` (653 lines, 22 methods)
3. **Output Formatters**: Extract from `cli.py` to new `output.py` module

When refactoring:
- Maintain backward compatibility
- Keep existing public API surface
- Add tests for extracted functions
- Update imports in `__init__.py` files

## Adding a New Validator

1. Create a new file in `src/vallm/validators/`
2. Inherit from `BaseValidator`
3. Implement required methods: `validate()`, `tier`, `name`, `weight`
4. Add tests in `tests/test_<validator>.py`
5. Register in `scoring._get_default_validators()` if it should be default

Example:

```python
# src/vallm/validators/my_validator.py
from vallm.validators.base import BaseValidator
from vallm.scoring import ValidationResult, Issue, Severity

class MyValidator(BaseValidator):
    tier = 2  # 1=fast, 2=thorough, 3=LLM
    name = "my_validator"
    weight = 1.0

    def validate(self, proposal, context):
        # Your validation logic
        issues = []
        score = 1.0

        return ValidationResult(
            validator=self.name,
            score=score,
            weight=self.weight,
            issues=issues,
        )
```

## Pull Request Process

1. **Before starting**: Check [TODO.md](TODO.md) and open issues
2. **Branch naming**: `feature/description` or `fix/description`
3. **Commits**: Use clear, descriptive commit messages
4. **Tests**: Add tests for new functionality
5. **Documentation**: Update README.md and relevant docs
6. **Changelog**: Add entry to [CHANGELOG.md](CHANGELOG.md)

### PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Code formatted (`ruff format .`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`mypy src/vallm`)
- [ ] Security scan passes (`bandit -r src/vallm`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

## Reporting Issues

When reporting bugs, please include:

- Python version (`python --version`)
- vallm version (`pip show vallm`)
- Operating system
- Minimal code example to reproduce
- Expected vs actual behavior

For feature requests, describe:

- Use case
- Proposed API/syntax
- Similar features in other tools (if any)

## Code of Conduct

- Be respectful and constructive
- Focus on technical merits
- Welcome newcomers
- Assume good intentions

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Contact: tom@sapletta.com

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
