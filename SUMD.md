# vallm

A complete toolkit for validating LLM-generated code

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Intent](#intent)

## Metadata

- **name**: `vallm`
- **version**: `0.1.74`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, app.doql.css, pyqual.yaml, goal.yaml, .env.example, project/(1 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.css`)

```css markpact:doql path=app.doql.css
app {
  name: "vallm";
  version: "0.1.75";
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="vallm"] {

}

workflow[name="venv"] {
  trigger: "manual";
  step-1: run cmd=if [ ! -x "$(PYTHON)" ]; then \;
  step-2: run cmd=echo "Creating virtual environment in $(VENV)..."; \;
  step-3: run cmd=python3 -m venv "$(VENV)"; \;
  step-4: run cmd=fi;
}

workflow[name="install"] {
  trigger: "manual";
  step-1: run cmd=$(PIP) install -e .;
  step-2: run cmd=echo "✓ code2llm installed with TOON format support";
}

workflow[name="dev-install"] {
  trigger: "manual";
  step-1: run cmd=$(PIP) install -e ".[dev]";
  step-2: run cmd=echo "✓ code2llm installed with dev dependencies";
}

workflow[name="test"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pytest tests/ -v --tb=short;
}

workflow[name="test-fast"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pytest -m "not slow and not integration" -v --tb=short -n auto;
}

workflow[name="test-slow"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pytest -m "slow" -v --tb=short;
}

workflow[name="test-integration"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pytest -m "integration" -v --tb=short;
}

workflow[name="test-unit"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pytest -m "unit" -v --tb=short;
}

workflow[name="test-cov"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pytest tests/ --cov=code2llm --cov-report=html --cov-report=term 2>/dev/null || echo "No tests yet";
}

workflow[name="test-toon"] {
  trigger: "manual";
  step-1: run cmd=echo "🎯 Testing TOON format...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./test_toon -m hybrid -f toon;
  step-3: run cmd=$(PYTHON) validate_toon.py test_toon/analysis.toon;
  step-4: run cmd=echo "✓ TOON format test complete";
}

workflow[name="validate-toon"] {
  trigger: "manual";
  step-1: depend target=test-toon;
}

workflow[name="test-all-formats"] {
  trigger: "manual";
  step-1: run cmd=echo "📊 Testing all output formats...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./test_all -m hybrid -f all;
  step-3: run cmd=$(PYTHON) validate_toon.py test_all/analysis.toon;
  step-4: run cmd=echo "✓ All formats test complete";
}

workflow[name="test-comprehensive"] {
  trigger: "manual";
  step-1: run cmd=echo "🚀 Running comprehensive test suite...";
  step-2: run cmd=bash project.sh;
  step-3: run cmd=echo "✓ Comprehensive tests complete";
}

workflow[name="lint"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m flake8 code2llm/ --max-line-length=100 --ignore=E203,W503 2>/dev/null || echo "flake8 not installed";
  step-2: run cmd=$(PYTHON) -m black --check code2llm/ 2>/dev/null || echo "black not installed";
  step-3: run cmd=echo "✓ Linting complete";
}

workflow[name="format"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m black code2llm/ --line-length=100 2>/dev/null || echo "black not installed, run: pip install black";
  step-2: run cmd=echo "✓ Code formatted";
}

workflow[name="typecheck"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m mypy code2llm/ --ignore-missing-imports 2>/dev/null || echo "mypy not installed";
}

workflow[name="check"] {
  trigger: "manual";
  step-1: run cmd=echo "✓ All checks passed";
}

workflow[name="run"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m code2llm ../python/stts_core -v -o ./output;
}

workflow[name="analyze"] {
  trigger: "manual";
  step-1: run cmd=echo "🎯 Running TOON format analysis on current project...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./analysis -m hybrid -f toon;
  step-3: run cmd=$(PYTHON) validate_toon.py analysis/analysis.toon;
  step-4: run cmd=echo "✓ TOON analysis complete - check analysis/analysis.toon";
}

workflow[name="analyze-all"] {
  trigger: "manual";
  step-1: run cmd=echo "📊 Running analysis with all formats...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./analysis_all -m hybrid -f all;
  step-3: run cmd=$(PYTHON) validate_toon.py analysis_all/analysis.toon;
  step-4: run cmd=echo "✓ All formats analysis complete - check analysis_all/";
}

workflow[name="toon-demo"] {
  trigger: "manual";
  step-1: run cmd=echo "🎯 Quick TOON format demo...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./demo -m hybrid -f toon;
  step-3: run cmd=echo "📁 Generated: demo/analysis.toon";
  step-4: run cmd=echo "📊 Size: $$(du -h demo/analysis.toon | cut -f1)";
  step-5: run cmd=echo "🔍 Preview:";
  step-6: run cmd=head -20 demo/analysis.toon;
}

workflow[name="toon-compare"] {
  trigger: "manual";
  step-1: run cmd=echo "📊 Comparing TOON vs YAML formats...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./compare -m hybrid -f toon,yaml;
  step-3: run cmd=echo "📁 Files generated:";
  step-4: run cmd=echo "  - TOON:  compare/analysis.toon  ($$(du -h compare/analysis.toon | cut -f1))";
  step-5: run cmd=echo "  - YAML:  compare/analysis.yaml  ($$(du -h compare/analysis.yaml | cut -f1))";
  step-6: run cmd=echo "  - Ratio: $$(echo "scale=1; $$(du -k compare/analysis.yaml | cut -f1) / $$(du -k compare/analysis.toon | cut -f1)" | bc)x smaller";
  step-7: run cmd=$(PYTHON) validate_toon.py compare/analysis.yaml compare/analysis.toon;
}

workflow[name="toon-validate"] {
  trigger: "manual";
  step-1: run cmd=echo "🔍 Validating TOON format structure...";
  step-2: run cmd=$(PYTHON) validate_toon.py analysis/analysis.toon 2>/dev/null || $(PYTHON) validate_toon.py test_toon/analysis.toon 2>/dev/null || echo "Run 'make test-toon' first";
}

workflow[name="build"] {
  trigger: "manual";
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
  step-2: run cmd=$(PYTHON) -m build;
  step-3: run cmd=echo "✓ Build complete - check dist/";
}

workflow[name="publish-test"] {
  trigger: "manual";
  step-1: run cmd=echo "🚀 Publishing to TestPyPI...";
  step-2: run cmd=bash -c 'if [ -z "$${TWINE_USERNAME}" ] && [ -z "$${TWINE_PASSWORD}" ] && [ -z "$${PYPI_API_TOKEN}" ]; then \;
  step-3: run cmd=echo "⚠️  No PyPI credentials found. Set TWINE_USERNAME and TWINE_PASSWORD or PYPI_API_TOKEN"; \;
  step-4: run cmd=echo "   Example: TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-xxx make publish-test"; \;
  step-5: run cmd=echo "   Skipping publish-test."; \;
  step-6: run cmd=else \;
  step-7: run cmd=$(PYTHON) -m venv publish-test-env && \;
  step-8: run cmd=publish-test-env/bin/pip install twine && \;
  step-9: run cmd=publish-test-env/bin/python -m twine upload --repository testpypi dist/* && \;
  step-10: run cmd=rm -rf publish-test-env && \;
  step-11: run cmd=echo "✓ Published to TestPyPI"; \;
  step-12: run cmd=fi';
}

workflow[name="bump-patch"] {
  trigger: "manual";
  step-1: run cmd=echo "🔢 Bumping patch version...";
  step-2: run cmd=$(PYTHON) scripts/bump_version.py patch 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually";
}

workflow[name="bump-minor"] {
  trigger: "manual";
  step-1: run cmd=echo "🔢 Bumping minor version...";
  step-2: run cmd=$(PYTHON) scripts/bump_version.py minor 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually";
}

workflow[name="bump-major"] {
  trigger: "manual";
  step-1: run cmd=echo "🔢 Bumping major version...";
  step-2: run cmd=$(PYTHON) scripts/bump_version.py major 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually";
}

workflow[name="publish"] {
  trigger: "manual";
  step-1: run cmd=echo "🚀 Publishing to PyPI...";
  step-2: run cmd=bash -c 'if [ -z "$${TWINE_USERNAME}" ] && [ -z "$${TWINE_PASSWORD}" ] && [ -z "$${PYPI_API_TOKEN}" ]; then \;
  step-3: run cmd=echo "⚠️  No PyPI credentials found. Set TWINE_USERNAME and TWINE_PASSWORD or PYPI_API_TOKEN"; \;
  step-4: run cmd=echo "   Example: TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-xxx make publish"; \;
  step-5: run cmd=echo "   Skipping publish."; \;
  step-6: run cmd=else \;
  step-7: run cmd=echo "🔢 Bumping patch version..."; \;
  step-8: run cmd=$(MAKE) bump-patch; \;
  step-9: run cmd=echo "🔨 Rebuilding package with new version..."; \;
  step-10: run cmd=$(MAKE) build; \;
  step-11: run cmd=echo "📦 Publishing to PyPI..."; \;
  step-12: run cmd=$(PYTHON) -m venv publish-env; \;
  step-13: run cmd=publish-env/bin/pip install twine; \;
  step-14: run cmd=publish-env/bin/python -m twine upload dist/*; \;
  step-15: run cmd=rm -rf publish-env; \;
  step-16: run cmd=echo "✓ Published to PyPI"; \;
  step-17: run cmd=fi';
}

workflow[name="mermaid-png"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) mermaid_to_png.py --batch output output;
}

workflow[name="install-mermaid"] {
  trigger: "manual";
  step-1: run cmd=npm install -g @mermaid-js/mermaid-cli;
}

workflow[name="check-mermaid"] {
  trigger: "manual";
  step-1: run cmd=echo "Checking available Mermaid renderers...";
  step-2: run cmd=which mmdc > /dev/null && echo "✓ mmdc (mermaid-cli)" || echo "✗ mmdc (run: npm install -g @mermaid-js/mermaid-cli)";
  step-3: run cmd=which npx > /dev/null && echo "✓ npx (for @mermaid-js/mermaid-cli)" || echo "✗ npx (install Node.js)";
  step-4: run cmd=which puppeteer > /dev/null && echo "✓ puppeteer" || echo "✗ puppeteer (run: npm install -g puppeteer)";
}

workflow[name="clean"] {
  trigger: "manual";
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
  step-2: run cmd=rm -rf .pytest_cache .coverage htmlcov/;
  step-3: run cmd=rm -rf code2llm/__pycache__ code2llm/*/__pycache__;
  step-4: run cmd=rm -rf test_* demo compare analysis analysis_all output_* 2>/dev/null || true;
  step-5: run cmd=find . -name "*.pyc" -delete 2>/dev/null || true;
  step-6: run cmd=find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true;
  step-7: run cmd=echo "✓ Cleaned build artifacts and test outputs";
}

workflow[name="clean-png"] {
  trigger: "manual";
  step-1: run cmd=rm -f output/*.png;
  step-2: run cmd=echo "✓ Cleaned PNG files";
}

workflow[name="quickstart"] {
  trigger: "manual";
  step-1: run cmd=echo "🚀 Quick Start with code2llm TOON format:";
  step-2: run cmd=echo "";
  step-3: run cmd=echo "1. Install:        make install";
  step-4: run cmd=echo "2. Test TOON:      make test-toon";
  step-5: run cmd=echo "3. Analyze:        make analyze";
  step-6: run cmd=echo "4. Compare:        make toon-compare";
  step-7: run cmd=echo "5. All formats:    make test-all-formats";
  step-8: run cmd=echo "";
  step-9: run cmd=echo "📖 For more: make help";
}

workflow[name="fmt"] {
  trigger: "manual";
  step-1: run cmd=ruff format .;
}

workflow[name="health"] {
  trigger: "manual";
  step-1: run cmd=docker compose ps;
  step-2: run cmd=docker compose exec app echo "Health check passed";
}

workflow[name="import-makefile-hint"] {
  trigger: "manual";
  step-1: run cmd=echo 'Run: taskfile import Makefile to import existing targets.';
}

workflow[name="help"] {
  trigger: "manual";
  step-1: run cmd=echo "code2llm - Python Code Flow Analysis Tool with LLM Integration and TOON;
  step-2: run cmd=echo "";
  step-3: run cmd=echo \"\U0001F680 Installation:\; 
  step-4: run cmd=echo "  make install       - Install package";
  step-5: run cmd=echo "  make dev-install   - Install with development dependencies";
  step-6: run cmd=echo "";
  step-7: run cmd=echo \"\U0001F9EA Testing:\; 
  step-8: run cmd=echo "  make test          - Run test suite";
  step-9: run cmd=echo "  make test-toon     - Test TOON format only";
  step-10: run cmd=echo "  make validate-toon - Validate TOON format output";
  step-11: run cmd=echo "  make test-all-formats - Test all output formats";
  step-12: run cmd=echo "";
  step-13: run cmd=echo \"\U0001F527 Code Quality:\; 
  step-14: run cmd=echo "  make lint          - Run linters (flake8, black --check)";
  step-15: run cmd=echo "  make format        - Format code with black";
  step-16: run cmd=echo "  make typecheck     - Run mypy type checking";
  step-17: run cmd=echo "  make check         - Run all quality checks";
  step-18: run cmd=echo "";
  step-19: run cmd=echo \"\U0001F4CA Analysis:\; 
  step-20: run cmd=echo "  make analyze       - Run analysis on current project (TOON format)";
  step-21: run cmd=echo "  make run           - Run with example arguments";
  step-22: run cmd=echo "  make analyze-all   - Run analysis with all formats";
  step-23: run cmd=echo "";
  step-24: run cmd=echo \"\U0001F3AF TOON Format:\; 
  step-25: run cmd=echo "  make toon-demo     - Quick TOON format demo";
  step-26: run cmd=echo "  make toon-compare  - Compare TOON vs YAML formats";
  step-27: run cmd=echo "  make toon-validate - Validate TOON format structure";
  step-28: run cmd=echo "";
  step-29: run cmd=echo \"\U0001F4E6 Building & Release:\; 
  step-30: run cmd=echo "  make build         - Build distribution packages";
  step-31: run cmd=echo "  make publish       - Publish to PyPI (with version bump)";
  step-32: run cmd=echo "  make publish-test  - Publish to TestPyPI";
  step-33: run cmd=echo "  make bump-patch    - Bump patch version";
  step-34: run cmd=echo "  make bump-minor    - Bump minor version";
  step-35: run cmd=echo "  make bump-major    - Bump major version";
  step-36: run cmd=echo "";
  step-37: run cmd=echo \"\U0001F3A8 Visualization:\; 
  step-38: run cmd=echo "  make mermaid-png   - Generate PNG from all Mermaid files";
  step-39: run cmd=echo "  make install-mermaid - Install Mermaid CLI renderer";
  step-40: run cmd=echo "  make check-mermaid - Check available Mermaid renderers";
  step-41: run cmd=echo "";
  step-42: run cmd=echo \"\U0001F9F9 Maintenance:\; 
  step-43: run cmd=echo "  make clean         - Remove build artifacts";
  step-44: run cmd=echo "  make clean-png     - Clean PNG files";
  step-45: run cmd=echo "";
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker;
  env_file: ".env";
}

workflow[name="all"] {
  trigger: "manual";
  step-1: run cmd=taskfile run install;
  step-2: run cmd=taskfile run lint;
  step-3: run cmd=taskfile run test;
}
```

## Interfaces

### CLI Entry Points

- `vallm`

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
version: '1'
name: vallm
description: Minimal Taskfile
variables:
  APP_NAME: vallm
environments:
  local:
    container_runtime: docker
    compose_command: docker compose
pipeline:
  python_version: "3.12"
  runner_image: ubuntu-latest
  branches: [main]
  cache: [~/.cache/pip]
  artifacts: [dist/]

  stages:
    - name: lint
      tasks: [lint]

    - name: test
      tasks: [test]

    - name: build
      tasks: [build]
      when: "branch:main"

tasks:
  install:
    desc: Install Python dependencies (editable)
    cmds:
    - pip install -e .[dev]
  test:
    desc: Run quality pipeline (pyqual)
    cmds:
    - pyqual run
  lint:
    desc: Check quality gates (pyqual)
    cmds:
    - pyqual check-gates
  fmt:
    desc: Auto-format with ruff
    cmds:
    - ruff format .
  check:
    desc: Run full pyqual pipeline with fix attempts
    cmds:
    - pyqual run --auto-fix
  build:
    desc: Build wheel + sdist (via pyqual pipeline)
    cmds:
    - pyqual run --stage publish || python -m build
  clean:
    desc: Remove build artefacts
    cmds:
    - rm -rf build/ dist/ *.egg-info
  help:
    desc: '[imported from Makefile] help'
    cmds:
    - echo "code2llm - Python Code Flow Analysis Tool with LLM Integration and TOON
      Format"
    - echo ""
    - "echo \"\U0001F680 Installation:\""
    - echo "  make install       - Install package"
    - echo "  make dev-install   - Install with development dependencies"
    - echo ""
    - "echo \"\U0001F9EA Testing:\""
    - echo "  make test          - Run test suite"
    - echo "  make test-toon     - Test TOON format only"
    - echo "  make validate-toon - Validate TOON format output"
    - echo "  make test-all-formats - Test all output formats"
    - echo ""
    - "echo \"\U0001F527 Code Quality:\""
    - echo "  make lint          - Run linters (flake8, black --check)"
    - echo "  make format        - Format code with black"
    - echo "  make typecheck     - Run mypy type checking"
    - echo "  make check         - Run all quality checks"
    - echo ""
    - "echo \"\U0001F4CA Analysis:\""
    - echo "  make analyze       - Run analysis on current project (TOON format)"
    - echo "  make run           - Run with example arguments"
    - echo "  make analyze-all   - Run analysis with all formats"
    - echo ""
    - "echo \"\U0001F3AF TOON Format:\""
    - echo "  make toon-demo     - Quick TOON format demo"
    - echo "  make toon-compare  - Compare TOON vs YAML formats"
    - echo "  make toon-validate - Validate TOON format structure"
    - echo ""
    - "echo \"\U0001F4E6 Building & Release:\""
    - echo "  make build         - Build distribution packages"
    - echo "  make publish       - Publish to PyPI (with version bump)"
    - echo "  make publish-test  - Publish to TestPyPI"
    - echo "  make bump-patch    - Bump patch version"
    - echo "  make bump-minor    - Bump minor version"
    - echo "  make bump-major    - Bump major version"
    - echo ""
    - "echo \"\U0001F3A8 Visualization:\""
    - echo "  make mermaid-png   - Generate PNG from all Mermaid files"
    - echo "  make install-mermaid - Install Mermaid CLI renderer"
    - echo "  make check-mermaid - Check available Mermaid renderers"
    - echo ""
    - "echo \"\U0001F9F9 Maintenance:\""
    - echo "  make clean         - Remove build artifacts"
    - echo "  make clean-png     - Clean PNG files"
    - echo ""
  venv:
    desc: '[imported from Makefile] venv'
    cmds:
    - if [ ! -x "$(PYTHON)" ]; then \
    - echo "Creating virtual environment in $(VENV)..."; \
    - python3 -m venv "$(VENV)"; \
    - fi
  dev-install:
    desc: '[imported from Makefile] dev-install'
    cmds:
    - $(PIP) install -e ".[dev]"
    - "echo \"\u2713 code2llm installed with dev dependencies\""
  test-fast:
    desc: '[imported from Makefile] test-fast'
    cmds:
    - $(PYTHON) -m pytest -m "not slow and not integration" -v --tb=short -n auto
  test-slow:
    desc: '[imported from Makefile] test-slow'
    cmds:
    - $(PYTHON) -m pytest -m "slow" -v --tb=short
  test-integration:
    desc: '[imported from Makefile] test-integration'
    cmds:
    - $(PYTHON) -m pytest -m "integration" -v --tb=short
  test-unit:
    desc: '[imported from Makefile] test-unit'
    cmds:
    - $(PYTHON) -m pytest -m "unit" -v --tb=short
  test-cov:
    desc: '[imported from Makefile] test-cov'
    cmds:
    - $(PYTHON) -m pytest tests/ --cov=code2llm --cov-report=html --cov-report=term
      2>/dev/null || echo "No tests yet"
  test-toon:
    desc: '[imported from Makefile] test-toon'
    cmds:
    - "echo \"\U0001F3AF Testing TOON format...\""
    - $(PYTHON) -m code2llm ./ -v -o ./test_toon -m hybrid -f toon
    - $(PYTHON) validate_toon.py test_toon/analysis.toon
    - "echo \"\u2713 TOON format test complete\""
  validate-toon:
    desc: '[imported from Makefile] validate-toon'
    deps:
    - test-toon
  test-all-formats:
    desc: '[imported from Makefile] test-all-formats'
    cmds:
    - "echo \"\U0001F4CA Testing all output formats...\""
    - $(PYTHON) -m code2llm ./ -v -o ./test_all -m hybrid -f all
    - $(PYTHON) validate_toon.py test_all/analysis.toon
    - "echo \"\u2713 All formats test complete\""
  test-comprehensive:
    desc: '[imported from Makefile] test-comprehensive'
    cmds:
    - "echo \"\U0001F680 Running comprehensive test suite...\""
    - bash project.sh
    - "echo \"\u2713 Comprehensive tests complete\""
  format:
    desc: '[imported from Makefile] format'
    cmds:
    - '$(PYTHON) -m black code2llm/ --line-length=100 2>/dev/null || echo "black not
      installed, run: pip install black"'
    - "echo \"\u2713 Code formatted\""
  typecheck:
    desc: '[imported from Makefile] typecheck'
    cmds:
    - $(PYTHON) -m mypy code2llm/ --ignore-missing-imports 2>/dev/null || echo "mypy
      not installed"
  check:
    desc: '[imported from Makefile] check'
    cmds:
    - "echo \"\u2713 All checks passed\""
    deps:
    - lint
    - typecheck
    - test
  run:
    desc: '[imported from Makefile] run'
    cmds:
    - $(PYTHON) -m code2llm ../python/stts_core -v -o ./output
  analyze:
    desc: '[imported from Makefile] analyze'
    cmds:
    - "echo \"\U0001F3AF Running TOON format analysis on current project...\""
    - $(PYTHON) -m code2llm ./ -v -o ./analysis -m hybrid -f toon
    - $(PYTHON) validate_toon.py analysis/analysis.toon
    - "echo \"\u2713 TOON analysis complete - check analysis/analysis.toon\""
  analyze-all:
    desc: '[imported from Makefile] analyze-all'
    cmds:
    - "echo \"\U0001F4CA Running analysis with all formats...\""
    - $(PYTHON) -m code2llm ./ -v -o ./analysis_all -m hybrid -f all
    - $(PYTHON) validate_toon.py analysis_all/analysis.toon
    - "echo \"\u2713 All formats analysis complete - check analysis_all/\""
  toon-demo:
    desc: '[imported from Makefile] toon-demo'
    cmds:
    - "echo \"\U0001F3AF Quick TOON format demo...\""
    - $(PYTHON) -m code2llm ./ -v -o ./demo -m hybrid -f toon
    - "echo \"\U0001F4C1 Generated: demo/analysis.toon\""
    - "echo \"\U0001F4CA Size: $$(du -h demo/analysis.toon | cut -f1)\""
    - "echo \"\U0001F50D Preview:\""
    - head -20 demo/analysis.toon
  toon-compare:
    desc: '[imported from Makefile] toon-compare'
    cmds:
    - "echo \"\U0001F4CA Comparing TOON vs YAML formats...\""
    - $(PYTHON) -m code2llm ./ -v -o ./compare -m hybrid -f toon,yaml
    - "echo \"\U0001F4C1 Files generated:\""
    - 'echo "  - TOON:  compare/analysis.toon  ($$(du -h compare/analysis.toon | cut
      -f1))"'
    - 'echo "  - YAML:  compare/analysis.yaml  ($$(du -h compare/analysis.yaml | cut
      -f1))"'
    - 'echo "  - Ratio: $$(echo "scale=1; $$(du -k compare/analysis.yaml | cut -f1)
      / $$(du -k compare/analysis.toon | cut -f1)" | bc)x smaller"'
    - $(PYTHON) validate_toon.py compare/analysis.yaml compare/analysis.toon
  toon-validate:
    desc: '[imported from Makefile] toon-validate'
    cmds:
    - "echo \"\U0001F50D Validating TOON format structure...\""
    - $(PYTHON) validate_toon.py analysis/analysis.toon 2>/dev/null || $(PYTHON) validate_toon.py
      test_toon/analysis.toon 2>/dev/null || echo "Run 'make test-toon' first"
  publish-test:
    desc: '[imported from Makefile] publish-test'
    cmds:
    - "echo \"\U0001F680 Publishing to TestPyPI...\""
    - bash -c 'if [ -z "$${TWINE_USERNAME}" ] && [ -z "$${TWINE_PASSWORD}" ] && [
      -z "$${PYPI_API_TOKEN}" ]; then \
    - "echo \"\u26A0\uFE0F  No PyPI credentials found. Set TWINE_USERNAME and TWINE_PASSWORD\
      \ or PYPI_API_TOKEN\"; \\"
    - 'echo "   Example: TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-xxx make publish-test";
      \'
    - echo "   Skipping publish-test."; \
    - else \
    - $(PYTHON) -m venv publish-test-env && \
    - publish-test-env/bin/pip install twine && \
    - publish-test-env/bin/python -m twine upload --repository testpypi dist/* &&
      \
    - rm -rf publish-test-env && \
    - "echo \"\u2713 Published to TestPyPI\"; \\"
    - fi'
    deps:
    - build
  bump-patch:
    desc: '[imported from Makefile] bump-patch'
    cmds:
    - "echo \"\U0001F522 Bumping patch version...\""
    - $(PYTHON) scripts/bump_version.py patch 2>/dev/null || echo "Create scripts/bump_version.py
      or edit pyproject.toml manually"
  bump-minor:
    desc: '[imported from Makefile] bump-minor'
    cmds:
    - "echo \"\U0001F522 Bumping minor version...\""
    - $(PYTHON) scripts/bump_version.py minor 2>/dev/null || echo "Create scripts/bump_version.py
      or edit pyproject.toml manually"
  bump-major:
    desc: '[imported from Makefile] bump-major'
    cmds:
    - "echo \"\U0001F522 Bumping major version...\""
    - $(PYTHON) scripts/bump_version.py major 2>/dev/null || echo "Create scripts/bump_version.py
      or edit pyproject.toml manually"
  publish:
    desc: '[imported from Makefile] publish'
    cmds:
    - "echo \"\U0001F680 Publishing to PyPI...\""
    - bash -c 'if [ -z "$${TWINE_USERNAME}" ] && [ -z "$${TWINE_PASSWORD}" ] && [
      -z "$${PYPI_API_TOKEN}" ]; then \
    - "echo \"\u26A0\uFE0F  No PyPI credentials found. Set TWINE_USERNAME and TWINE_PASSWORD\
      \ or PYPI_API_TOKEN\"; \\"
    - 'echo "   Example: TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-xxx make publish";
      \'
    - echo "   Skipping publish."; \
    - else \
    - "echo \"\U0001F522 Bumping patch version...\"; \\"
    - $(MAKE) bump-patch; \
    - "echo \"\U0001F528 Rebuilding package with new version...\"; \\"
    - $(MAKE) build; \
    - "echo \"\U0001F4E6 Publishing to PyPI...\"; \\"
    - $(PYTHON) -m venv publish-env; \
    - publish-env/bin/pip install twine; \
    - publish-env/bin/python -m twine upload dist/*; \
    - rm -rf publish-env; \
    - "echo \"\u2713 Published to PyPI\"; \\"
    - fi'
    deps:
    - build
  mermaid-png:
    desc: '[imported from Makefile] mermaid-png'
    cmds:
    - $(PYTHON) mermaid_to_png.py --batch output output
  install-mermaid:
    desc: '[imported from Makefile] install-mermaid'
    cmds:
    - npm install -g @mermaid-js/mermaid-cli
  check-mermaid:
    desc: '[imported from Makefile] check-mermaid'
    cmds:
    - echo "Checking available Mermaid renderers..."
    - "which mmdc > /dev/null && echo \"\u2713 mmdc (mermaid-cli)\" || echo \"\u2717\
      \ mmdc (run: npm install -g @mermaid-js/mermaid-cli)\""
    - "which npx > /dev/null && echo \"\u2713 npx (for @mermaid-js/mermaid-cli)\"\
      \ || echo \"\u2717 npx (install Node.js)\""
    - "which puppeteer > /dev/null && echo \"\u2713 puppeteer\" || echo \"\u2717 puppeteer\
      \ (run: npm install -g puppeteer)\""
  clean-png:
    desc: '[imported from Makefile] clean-png'
    cmds:
    - rm -f output/*.png
    - "echo \"\u2713 Cleaned PNG files\""
  quickstart:
    desc: '[imported from Makefile] quickstart'
    cmds:
    - "echo \"\U0001F680 Quick Start with code2llm TOON format:\""
    - echo ""
    - 'echo "1. Install:        make install"'
    - 'echo "2. Test TOON:      make test-toon"'
    - 'echo "3. Analyze:        make analyze"'
    - 'echo "4. Compare:        make toon-compare"'
    - 'echo "5. All formats:    make test-all-formats"'
    - echo ""
    - "echo \"\U0001F4D6 For more: make help\""
  health:
    desc: '[from doql] workflow: health'
    cmds:
    - docker compose ps
    - docker compose exec app echo "Health check passed"
  import-makefile-hint:
    desc: '[from doql] workflow: import-makefile-hint'
    cmds:
    - 'echo ''Run: taskfile import Makefile to import existing targets.'''
  all:
    desc: Run install, lint, test
    cmds:
    - taskfile run install
    - taskfile run lint
    - taskfile run test
  sumd:
    desc: Generate SUMD (Structured Unified Markdown Descriptor) for AI-aware project description
    cmds:
    - |
      echo "# $(basename $(pwd))" > SUMD.md
      echo "" >> SUMD.md
      echo "$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('description','Project description'))" 2>/dev/null || echo 'Project description')" >> SUMD.md
      echo "" >> SUMD.md
      echo "## Contents" >> SUMD.md
      echo "" >> SUMD.md
      echo "- [Metadata](#metadata)" >> SUMD.md
      echo "- [Architecture](#architecture)" >> SUMD.md
      echo "- [Dependencies](#dependencies)" >> SUMD.md
      echo "- [Source Map](#source-map)" >> SUMD.md
      echo "- [Intent](#intent)" >> SUMD.md
      echo "" >> SUMD.md
      echo "## Metadata" >> SUMD.md
      echo "" >> SUMD.md
      echo "- **name**: \`$(basename $(pwd))\`" >> SUMD.md
      echo "- **version**: \`$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('version','unknown'))" 2>/dev/null || echo 'unknown')\`" >> SUMD.md
      echo "- **python_requires**: \`>=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d. -f1,2)\`" >> SUMD.md
      echo "- **license**: $(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('license',{}).get('text','MIT'))" 2>/dev/null || echo 'MIT')" >> SUMD.md
      echo "- **ecosystem**: SUMD + DOQL + testql + taskfile" >> SUMD.md
      echo "- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, src/" >> SUMD.md
      echo "" >> SUMD.md
      echo "## Architecture" >> SUMD.md
      echo "" >> SUMD.md
      echo '```' >> SUMD.md
      echo "SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)" >> SUMD.md
      echo '```' >> SUMD.md
      echo "" >> SUMD.md
      echo "## Source Map" >> SUMD.md
      echo "" >> SUMD.md
      find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' -not -path './__pycache__/*' -not -path './.git/*' | head -50 | sed 's|^./||' | sed 's|^|- |' >> SUMD.md
      echo "Generated SUMD.md"
    - |
      python3 -c "
      import json, os, subprocess
      from pathlib import Path
      project_name = Path.cwd().name
      py_files = list(Path('.').rglob('*.py'))
      py_files = [f for f in py_files if not any(x in str(f) for x in ['.venv', 'venv', '__pycache__', '.git'])]
      data = {
          'project_name': project_name,
          'description': 'SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization',
          'files': [{'path': str(f), 'type': 'python'} for f in py_files[:100]]
      }
      with open('sumd.json', 'w') as f:
          json.dump(data, f, indent=2)
      print('Generated sumd.json')
      " 2>/dev/null || echo 'Python generation failed, using fallback'
  sumr:
    desc: Generate SUMR (Summary Report) with project metrics and health status
    cmds:
    - |
      echo "# $(basename $(pwd)) - Summary Report" > SUMR.md
      echo "" >> SUMR.md
      echo "SUMR - Summary Report for project analysis" >> SUMR.md
      echo "" >> SUMR.md
      echo "## Contents" >> SUMR.md
      echo "" >> SUMR.md
      echo "- [Metadata](#metadata)" >> SUMR.md
      echo "- [Quality Status](#quality-status)" >> SUMR.md
      echo "- [Metrics](#metrics)" >> SUMR.md
      echo "- [Refactoring Analysis](#refactoring-analysis)" >> SUMR.md
      echo "- [Intent](#intent)" >> SUMR.md
      echo "" >> SUMR.md
      echo "## Metadata" >> SUMR.md
      echo "" >> SUMR.md
      echo "- **name**: \`$(basename $(pwd))\`" >> SUMR.md
      echo "- **version**: \`$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('version','unknown'))" 2>/dev/null || echo 'unknown')\`" >> SUMR.md
      echo "- **generated_at**: \`$(date -Iseconds)\`" >> SUMR.md
      echo "" >> SUMR.md
      echo "## Quality Status" >> SUMR.md
      echo "" >> SUMR.md
      if [ -f pyqual.yaml ]; then
        echo "- **pyqual_config**: ✅ Present" >> SUMR.md
        echo "- **last_run**: $(stat -c %y .pyqual/pipeline.db 2>/dev/null | cut -d' ' -f1 || echo 'N/A')" >> SUMR.md
      else
        echo "- **pyqual_config**: ❌ Missing" >> SUMR.md
      fi
      echo "" >> SUMR.md
      echo "## Metrics" >> SUMR.md
      echo "" >> SUMR.md
      py_files=$(find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' | wc -l)
      echo "- **python_files**: $py_files" >> SUMR.md
      lines=$(find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' -exec cat {} \; 2>/dev/null | wc -l)
      echo "- **total_lines**: $lines" >> SUMR.md
      echo "" >> SUMR.md
      echo "## Refactoring Analysis" >> SUMR.md
      echo "" >> SUMR.md
      echo "Run \`code2llm ./ -f evolution\` for detailed refactoring queue." >> SUMR.md
      echo "Generated SUMR.md"
    - |
      python3 -c "
      import json, os, subprocess
      from pathlib import Path
      from datetime import datetime
      project_name = Path.cwd().name
      py_files = len([f for f in Path('.').rglob('*.py') if not any(x in str(f) for x in ['.venv', 'venv', '__pycache__', '.git'])])
      data = {
          'project_name': project_name,
          'report_type': 'SUMR',
          'generated_at': datetime.now().isoformat(),
          'metrics': {
              'python_files': py_files,
              'has_pyqual_config': Path('pyqual.yaml').exists()
          }
      }
      with open('SUMR.json', 'w') as f:
          json.dump(data, f, indent=2)
      print('Generated SUMR.json')
      " 2>/dev/null || echo 'Python generation failed, using fallback'
```

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: quality-loop-with-llx

  # Quality gates — pipeline iterates until ALL pass
  metrics:
    cc_max: 15           # cyclomatic complexity per function
    vallm_pass_min: 90   # vallm validation pass rate (%)
    coverage_min: 55     # test coverage (%) — realistic for current codebase
    # Security gates (uncomment to enable):
    # vuln_high_max: 0     # pip-audit high severity CVEs
    # bandit_high_max: 0   # bandit high severity issues
    # secrets_found_max: 0 # trufflehog/gitleaks secrets

  # Custom tool definitions
  custom_tools:
    - name: code2llm_vallm
      binary: .venv/bin/code2llm
      command: >-
        .venv/bin/code2llm {workdir} -f toon -o ./project --no-chunk
        --exclude .git venv dist __pycache__ .pytest_cache .mypy_cache .ruff_cache
        .code2llm_cache build *.egg-info
      output: ""
      allow_failure: false

    - name: vallm_src
      binary: .venv/bin/vallm
      command: >-
        .venv/bin/vallm batch {workdir}/src --recursive --format toon --output ./project
        --exclude .git,venv,dist,__pycache__,.pytest_cache,.mypy_cache,.ruff_cache,
        .code2llm_cache,build,*.egg-info
      output: ""
      allow_failure: false

    - name: vallm_verify
      binary: .venv/bin/vallm
      command: >-
        .venv/bin/vallm batch {workdir}/src --recursive --no-complexity --format toon --output ./project/verify
        --exclude .git,venv,dist,__pycache__,.pytest_cache,.mypy_cache,.ruff_cache,
        .code2llm_cache,build,*.egg-info
      output: ""
      allow_failure: false

  # Pipeline stages — use 'tool:' for built-in presets or 'run:' for custom
  stages:
    # Verify/install all tool dependencies before pipeline starts
    - name: setup
      run: |
        set -e
        echo "=== pyqual dependency check ==="
        # Python tools (pip)
        for pkg in code2llm vallm prefact llx pytest-cov goal; do
          if python -m pip show "$pkg" >/dev/null 2>&1; then
            echo "  ✓ $pkg"
          else
            echo "  ✗ $pkg — installing…"
            pip install -q "$pkg" || echo "  ⚠ $pkg install failed (optional)"
          fi
        done
        # Node tools (claude)
        if command -v claude >/dev/null 2>&1; then
          echo "  ✓ claude $(claude --version 2>/dev/null)"
        else
          echo "  ✗ claude — installing…"
          npm install -g --prefix="$HOME/.local" @anthropic-ai/claude-code 2>/dev/null \
            && echo "  ✓ claude installed" \
            || echo "  ⚠ claude install failed (fix stage will use llx fallback)"
        fi
        # Claude Code auth can be either:
        # - local OAuth session via `claude auth login`
        # - ANTHROPIC_API_KEY in CI/GitHub Actions
        # We only verify the CLI is available here.
        echo "=== setup done ==="
      when: first_iteration
      timeout: 300
#
#    - name: analyze
#      tool: code2llm_vallm
#      optional: true
#      when: first_iteration
#      timeout: 0
#
#    - name: validate
#      tool: vallm_src
#      optional: true
#      timeout: 0

    - name: lint
      tool: ruff
      optional: true

    - name: test
      run: .venv/bin/python -m pytest -q --tb=short --cov=src/vallm --cov-report=term-missing --cov-report=json:.pyqual/coverage.json
      when: always

    - name: prefact
      tool: prefact
      optional: true
      when: metrics_fail
      timeout: 900

    # # Claude Code fix — uses Claude Code CLI (Sonnet 4.5) in non-interactive mode
    # # Auth: `claude auth login` (local) or ANTHROPIC_API_KEY (CI)
    # - name: claude_fix
    #   run: |
    #     export PATH="$HOME/.local/bin:$PATH"
    #     ERRORS=""
    #     [ -f .pyqual/errors.json ] && ERRORS=$(cat .pyqual/errors.json)
    #     [ -f TODO.md ] && ERRORS="$ERRORS
    #     $(cat TODO.md)"
    #     if timeout 900 claude -p "Fix all quality gate failures in this Python project. Apply changes directly.
    #
    #     $ERRORS" \
    #       --model sonnet \
    #       --allowedTools "Edit,Read,Write,Bash(git diff),Bash(python),Bash(pytest -x)" \
    #       --output-format text; then
    #       echo "Claude Code fix completed."
    #     else
    #       rc=$?
    #       echo "Claude Code exited with $rc (timeout=900s); falling back to llx fix."
    #       llx fix . --apply --errors .pyqual/errors.json --verbose
    #     fi
    #   when: metrics_fail
    #   timeout: 1200

    - name: fix
      tool: llx-fix
      optional: true
      when: metrics_fail
      timeout: 1800

    - name: verify
      tool: vallm_verify
      optional: true
      when: after_fix
      timeout: 300

    # Simple git push (goal push had "Argument list too long" issue with many files)
    - name: push
      run: |
        if [ -n "$(git status --porcelain)" ]; then
          git add -A
          git commit -m "chore: pyqual auto-commit [skip ci]" 2>/dev/null || true
          git push origin HEAD
        else
          echo "No changes to push"
        fi
      when: metrics_pass
      optional: true
      timeout: 120

    - name: publish
      run: make publish
      when: metrics_pass
      optional: true
      timeout: 300

    # Generate comprehensive markdown report with Mermaid diagram and ASCII flow
    - name: markdown_report
      run: python3 -m pyqual.report_generator
      when: always
      optional: true
      timeout: 30

  # Loop behavior
  loop:
    max_iterations: 3
    on_fail: report      # report | create_ticket | block

  # Environment (optional)
  env:
    LLM_MODEL: openrouter/x-ai/grok-code-fast-1
    LLX_DEFAULT_TIER: balanced
    LLX_VERBOSE: true
```

## Configuration

```yaml
project:
  name: vallm
  version: 0.1.74
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
pluggy>=1.6
pydantic>=2.12
pydantic-settings>=2.13
typer>=0.12
rich>=14.3
tree-sitter>=0.25
tree-sitter-language-pack>=1.4
radon>=6.0
lizard>=1.21
pyflakes>=3.4
```

### Development

```text markpact:deps python scope=dev
pytest>=9.0
pytest-cov>=7.0
ruff>=0.15
tox>=4.0
goal>=2.1.174
costs>=0.1.48
pfix>=0.1.72
pyqual>=0.1.59
```

## Deployment

```bash markpact:run
pip install vallm

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VALLM_DEFAULT_TOON_FILENAME` | `validation.toon.yaml` | Output file configurations |
| `VALLM_DEFAULT_JSON_FILENAME` | `validation.json` |  |
| `VALLM_DEFAULT_YAML_FILENAME` | `validation.yaml` |  |
| `VALLM_DEFAULT_TXT_FILENAME` | `validation.txt` |  |
| `VALLM_OUTPUT_FORMAT` | `rich` | Default behaviors |
| `VALLM_DEFAULT_LANGUAGE` | `python` |  |
| `VALLM_PASS_THRESHOLD` | `0.8` | Scoring thresholds |
| `VALLM_REVIEW_THRESHOLD` | `0.5` |  |
| `VALLM_ENABLE_SYNTAX` | `true` | Validator toggles |
| `VALLM_ENABLE_IMPORTS` | `true` |  |
| `VALLM_ENABLE_COMPLEXITY` | `true` |  |
| `VALLM_ENABLE_SECURITY` | `false` |  |
| `VALLM_ENABLE_REGRESSION` | `false` |  |
| `VALLM_ENABLE_SEMANTIC` | `false` |  |
| `VALLM_MAX_CYCLOMATIC_COMPLEXITY` | `15` | Complexity limits |
| `VALLM_MAX_COGNITIVE_COMPLEXITY` | `20` |  |
| `VALLM_MAX_FUNCTION_LENGTH` | `100` |  |
| `VALLM_LLM_PROVIDER` | `ollama` | LLM settings (for semantic validator) |
| `VALLM_LLM_MODEL` | `qwen2.5-coder:7b` |  |
| `VALLM_LLM_BASE_URL` | `http://localhost:11434` |  |
| `VALLM_LLM_TEMPERATURE` | `0.1` |  |
| `VALLM_SANDBOX_BACKEND` | `subprocess` | Sandbox settings |
| `VALLM_SANDBOX_TIMEOUT` | `30` |  |
| `VALLM_SANDBOX_MEMORY_LIMIT` | `256m` |  |
| `VALLM_SEMANTIC_CACHE_ENABLED` | `true` | Cache settings |
| `VALLM_SEMANTIC_CACHE_TTL` | `3600` |  |
| `VALLM_MAX_CONCURRENT_VALIDATIONS` | `4` | Performance settings |
| `VALLM_TIMEOUT_SECONDS` | `300` |  |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`vallm`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/matplotlib/__init__.py:__version__`

## Makefile Targets

- `VENV`
- `PYTHON`
- `PIP`
- `help` — Default target
- `venv`
- `VENV_TARGETS`
- `install`
- `dev-install`
- `test`
- `test-fast` — Fast tests - exclude slow and integration tests
- `test-slow` — Slow tests only
- `test-integration` — Integration tests only
- `test-unit` — Unit tests only
- `test-cov`
- `test-toon`
- `validate-toon`
- `test-all-formats`
- `test-comprehensive`
- `lint`
- `format`
- `typecheck`
- `check`
- `run`
- `analyze`
- `analyze-all`
- `toon-demo`
- `toon-compare`
- `toon-validate`
- `build`
- `publish-test`
- `bump-patch`
- `bump-minor`
- `bump-major`
- `publish`
- `mermaid-png`
- `install-mermaid`
- `check-mermaid`
- `clean`
- `clean-png`
- `quickstart`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# vallm | 116f 14651L | shell:11,python:101,javascript:4 | 2026-04-19
# stats: 480 func | 0 cls | 116 mod | CC̄=3.3 | critical:2 | cycles:0
# alerts[5]: fan-out process_ticket_with_redsl=20; fan-out main=19; fan-out run_autonomous_workflow=19; fan-out analyze_with_code2llm=17; CC main=16
# hotspots[5]: process_ticket_with_redsl fan=20; run_autonomous_workflow fan=19; main fan=19; analyze_with_code2llm fan=17; analyze_with_code2llm fan=16
# evolution: CC̄ 3.4→3.3 (improved -0.1)
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[116]:
  backend/routers/tickets/__init__.py,19
  backend/routers/tickets/crud.py,187
  backend/routers/tickets/models.py,96
  backend/routers/tickets/redsl.py,243
  backend/routers/tickets/webhook.py,92
  examples/__init__.py,1
  examples/01_basic_validation/main.py,77
  examples/02_ast_comparison/main.py,118
  examples/03_security_check/main.py,118
  examples/04_graph_analysis/main.py,158
  examples/05_llm_semantic_review/main.py,125
  examples/05_llm_semantic_review/main_template.py,74
  examples/06_multilang_validation/main.py,217
  examples/06_multilang_validation/main_template.py,74
  examples/07_multi_language/main.py,327
  examples/08_code2llm_integration/main.py,250
  examples/09_code2logic_integration/main.py,298
  examples/10_mcp_ollama_demo/docker-entrypoint.sh,35
  examples/10_mcp_ollama_demo/legacy_code/order_processor.py,131
  examples/10_mcp_ollama_demo/mcp_demo.py,398
  examples/10_mcp_ollama_demo/refactored_output.py,127
  examples/10_mcp_ollama_demo/run.sh,260
  examples/11_claude_code_autonomous/claude_autonomous_demo.py,660
  examples/11_claude_code_autonomous/docker-entrypoint.sh,30
  examples/11_claude_code_autonomous/legacy_code/data_processor.py,224
  examples/11_claude_code_autonomous/run.sh,232
  examples/12_ollama_simple_demo/best_version.py,22
  examples/12_ollama_simple_demo/docker-entrypoint.sh,31
  examples/12_ollama_simple_demo/iteration_1.py,22
  examples/12_ollama_simple_demo/iteration_2.py,22
  examples/12_ollama_simple_demo/legacy_code/simple_buggy.py,112
  examples/12_ollama_simple_demo/ollama_simple_demo.py,338
  examples/12_ollama_simple_demo/run.sh,201
  examples/12_ollama_simple_demo/utils/__init__.py,17
  examples/12_ollama_simple_demo/utils/calculate_total.py,25
  examples/12_ollama_simple_demo/utils/load_config.py,19
  examples/12_ollama_simple_demo/utils/main.py,32
  examples/12_ollama_simple_demo/utils/process_user_input.py,45
  examples/12_ollama_simple_demo/utils/save_data.py,20
  examples/13_batch_processing/main.py,138
  examples/14_api_advanced/main.py,241
  examples/15_cli_usage/main.py,255
  examples/16_configuration/main.py,267
  examples/cycle-test/full-cycle.sh,259
  examples/cycle-test/validate-steps.sh,162
  examples/mcp_demo.py,206
  examples/run.sh,133
  examples/utils/__init__.py,195
  examples/utils/extract_code_from_response.py,32
  examples/utils/extraction.py,79
  examples/utils/logging_utils.py,89
  examples/utils/save_analysis_data.py,25
  examples/utils/validation_runner.py,104
  frontend/e2e/gui-login-enhanced.spec.js,61
  frontend/e2e/loginTestHelpers.js,98
  frontend/src/components/RedslHealthCard.jsx,49
  frontend/src/components/RedslHealthCard.parts.jsx,95
  mcp/__init__.py,1
  mcp/server/__init__.py,1
  mcp/server/_tools_vallm.py,464
  mcp/server/self_server.py,185
  mcp_server.py,28
  project.sh,37
  scripts/bump_version.py,78
  scripts/test_docker_installation.sh,106
  src/vallm/__init__.py,19
  src/vallm/__main__.py,5
  src/vallm/cli/__init__.py,45
  src/vallm/cli/batch_constants.py,23
  src/vallm/cli/batch_processor.py,5
  src/vallm/cli/batch_processor_files.py,25
  src/vallm/cli/batch_processor_filter.py,25
  src/vallm/cli/batch_processor_impl.py,487
  src/vallm/cli/batch_processor_patterns.py,126
  src/vallm/cli/batch_processor_validation.py,78
  src/vallm/cli/batch_utils.py,22
  src/vallm/cli/command_handlers.py,345
  src/vallm/cli/output_formatters/__init__.py,79
  src/vallm/cli/output_formatters/base.py,19
  src/vallm/cli/output_formatters/batch.py,315
  src/vallm/cli/output_formatters/shared.py,63
  src/vallm/cli/output_formatters/single.py,80
  src/vallm/cli/output_formatters/utils.py,11
  src/vallm/config.py,122
  src/vallm/core/__init__.py,3
  src/vallm/core/ast_compare.py,142
  src/vallm/core/gitignore.py,272
  src/vallm/core/graph_diff.py,104
  src/vallm/core/languages.py,227
  src/vallm/core/proposal.py,37
  src/vallm/hookspecs.py,33
  src/vallm/sandbox/__init__.py,1
  src/vallm/sandbox/runner.py,144
  src/vallm/scoring.py,218
  src/vallm/validators/__init__.py,1
  src/vallm/validators/base.py,21
  src/vallm/validators/complexity.py,183
  src/vallm/validators/file_cache.py,82
  src/vallm/validators/imports/__init__.py,25
  src/vallm/validators/imports/base.py,70
  src/vallm/validators/imports/c_imports.py,88
  src/vallm/validators/imports/factory.py,43
  src/vallm/validators/imports/go_imports.py,84
  src/vallm/validators/imports/java_imports.py,68
  src/vallm/validators/imports/javascript_imports.py,118
  src/vallm/validators/imports/python_imports.py,225
  src/vallm/validators/imports/rust_imports.py,78
  src/vallm/validators/imports/utils.py,166
  src/vallm/validators/imports/wrapper.py,30
  src/vallm/validators/lint.py,182
  src/vallm/validators/logical.py,142
  src/vallm/validators/regression.py,265
  src/vallm/validators/security.py,255
  src/vallm/validators/semantic.py,302
  src/vallm/validators/semantic_cache.py,187
  src/vallm/validators/syntax.py,96
D:
  examples/13_batch_processing/main.py:
    e: main
    main()
  frontend/src/components/RedslHealthCard.jsx:
    i: ../api,./RedslHealthCard.parts,react
    e: RedslHealthCard,handleRefactor,result,h
    RedslHealthCard()
    handleRefactor()
    result()
    h()
  backend/routers/tickets/redsl.py:
    e: process_ticket_with_redsl,_create_pr_for_ticket,get_ticket_processing_status
    process_ticket_with_redsl(ticket_id;data;background_tasks;user;db)
    _create_pr_for_ticket(ticket_id;repo;provider;project_path;decisions;files_modified;token;tenant_id)
    get_ticket_processing_status(ticket_id;user;db)
  frontend/src/components/RedslHealthCard.parts.jsx:
    i: ../constants,./GradeCircle
    e: MetricRow,ok,StatusChecking,StatusUnavailable,StatusLoading,StatusError,HealthContent,grade,score
    MetricRow()
    ok()
    StatusChecking()
    StatusUnavailable()
    StatusLoading()
    StatusError()
    HealthContent()
    grade()
    score()
  src/vallm/validators/imports/python_imports.py:
    e: PythonImportValidator,_collect_guarded_lines,_get_local_modules
    PythonImportValidator(BaseImportValidator): validate(2),_relative_import_exists(3),extract_imports(1),module_exists(1),get_language(0),_get_error_message(1),_get_rule_name(0)  # Python-specific import validator...
    _collect_guarded_lines(tree)
    _get_local_modules()
  src/vallm/validators/imports/utils.py:
    e: _is_gitignored,_should_skip_dir,_should_skip_entry,walk,validate_import_path
    _is_gitignored(path;project_root;gitignore_matcher)
    _should_skip_dir(name;skip_tests;skip_hidden)
    _should_skip_entry(path;name;project_root;gitignore_matcher;skip_tests;skip_hidden)
    walk(root;project_root;gitignore_matcher;skip_tests;skip_hidden;max_depth;current_depth)
    validate_import_path(import_path;source_file;project_root;known_modules;stdlib_modules)
  src/vallm/cli/batch_processor_impl.py:
    e: BatchProcessor
    BatchProcessor: __init__(1),process_batch(10),output_batch_results(5),_load_gitignore_parser(1),_build_file_list(2),_parse_filter_patterns(2),_should_exclude_file(2),_matches_include_pattern(2),_load_vallmignore(0),_filter_files(5),_handle_no_files_found(1),_show_validation_start(2),_read_file_text(1),_detect_file_language(1),_show_progress(4),_handle_validation_result(7),_show_verbose_output(3),_process_files(6),_process_files_parallel(4),_validate_single_file(2),_validate_single_file_sequential(3),_process_files_sequential(6)  # Handles batch validation of multiple files...
  examples/11_claude_code_autonomous/claude_autonomous_demo.py:
    e: Colors,log_section,log_step,log_code,analyze_with_code2llm,call_claude_code,validate_with_vallm,run_runtime_tests,create_basic_tests,generate_claude_prompt,generate_feedback_prompt,run_autonomous_workflow,main
    Colors:
    log_section(title)
    log_step(step;description)
    log_code(label;code;max_lines)
    analyze_with_code2llm(code_path)
    call_claude_code(prompt;model;temperature)
    validate_with_vallm(code;description)
    run_runtime_tests(code_path;test_file)
    create_basic_tests(code_path;test_file)
    generate_claude_prompt(code;analysis;iteration)
    generate_feedback_prompt(current_code;validation;test_results;analysis)
    run_autonomous_workflow(code_path;max_iterations)
    main()
  examples/utils/__init__.py:
    e: save_analysis_data,run_validation_examples,validate_code_example,print_summary
    save_analysis_data(example_name;result_data)
    run_validation_examples(example_name;good_code;bad_code;complex_code;settings)
    validate_code_example(name;code;settings;all_results;include_issue_details)
    print_summary(all_results)
  examples/10_mcp_ollama_demo/mcp_demo.py:
    e: Colors,log_section,log_step,log_code,analyze_with_code2llm,validate_with_vallm,call_ollama,generate_refactoring_prompt,run_mcp_workflow,main
    Colors:
    log_section(title)
    log_step(step;description)
    log_code(label;code;max_lines)
    analyze_with_code2llm(code_path)
    validate_with_vallm(code;description)
    call_ollama(prompt;model;temperature)
    generate_refactoring_prompt(code;analysis)
    run_mcp_workflow(code_path;max_iterations)
    main()
  examples/utils/validation_runner.py:
    e: run_validation_examples
    run_validation_examples(example_name;good_code;bad_code;complex_code;settings)
  src/vallm/validators/complexity.py:
    e: ComplexityValidator
    ComplexityValidator(BaseValidator): __init__(1),validate(2),_check_python_complexity(1),_check_lizard(3)  # Tier 2: Cyclomatic complexity, maintainability index, and fu...
  mcp/server/_tools_vallm.py:
    e: _format_issue,_compute_verdict,_run_validators,_build_pipeline_response,_build_validator_response,_build_error_response,validate_syntax,validate_imports,validate_security,validate_code,handle_validate_syntax,handle_validate_imports,handle_validate_security,handle_validate_code
    _format_issue(issue)
    _compute_verdict(overall_score;error_count)
    _run_validators(proposal;enable_syntax;enable_imports;enable_security;enable_complexity;enable_regression;reference_code)
    _build_pipeline_response(results;total_weight;verdict;all_issues)
    _build_validator_response(result;validator_name)
    _build_error_response(error;validator_name)
    validate_syntax(code;language;filename)
    validate_imports(code;language;filename)
    validate_security(code;language;filename)
    validate_code(code;language;filename;reference_code;enable_syntax;enable_imports;enable_security;enable_complexity;enable_regression)
    handle_validate_syntax(params)
    handle_validate_imports(params)
    handle_validate_security(params)
    handle_validate_code(params)
  examples/05_llm_semantic_review/main.py:
    e: main
    main()
  examples/07_multi_language/main.py:
    e: test_language_detection,validate_single_language,validate_all_languages,save_results,print_language_info,main
    test_language_detection()
    validate_single_language(lang_name;code;is_bad)
    validate_all_languages()
    save_results(results)
    print_language_info()
    main()
  src/vallm/core/gitignore.py:
    e: GitignoreParser,load_gitignore,get_default_excludes,create_default_gitignore_parser,should_exclude
    GitignoreParser: __init__(1),_parse(1),matches(1),_match_pattern(3),_fnmatch(2),_pattern_to_regex(1)  # Parse .gitignore files and match paths against patterns...
    load_gitignore(path)
    get_default_excludes()
    create_default_gitignore_parser()
    should_exclude(path;gitignore_parser;use_defaults)
  examples/09_code2logic_integration/main.py:
    e: analyze_with_code2logic,validate_with_vallm,build_call_graph,generate_report,visualize_flow,main
    analyze_with_code2logic(code)
    validate_with_vallm(code)
    build_call_graph(code)
    generate_report(code2logic_result;vallm_result;graph_result;output_path)
    visualize_flow(code;output_path)
    main()
  examples/11_claude_code_autonomous/legacy_code/data_processor.py:
    e: DataProcessor,ReportGenerator,load_config,init_database,main
    DataProcessor: __init__(0),process_user_data(1),calculate_metrics(1),export_data(2),validate_email(1),validate_email_again(1),process_with_external_api(1),complex_calculation(10),unused_function(0),another_unused_function(2)  # Data processor with multiple responsibilities - violates SRP...
    ReportGenerator: __init__(1),generate_report(0),export_report(1)  # Report generator with tight coupling to DataProcessor...
    load_config()
    init_database()
    main()
  examples/10_mcp_ollama_demo/legacy_code/order_processor.py:
    e: OrderManager,process_order,load_config,save_data,calculate,validate_email_1,validate_email_2,calculate_shipping,dead_code
    OrderManager: __init__(0),add_order(1),execute_query(1),process_payment(2),send_email(3),get_stats(0)  # Class with mixed responsibilities - SOLID violation...
    process_order(data)
    load_config()
    save_data(data;filename)
    calculate(x;y;z;a;b;c)
    validate_email_1(email)
    validate_email_2(email)
    calculate_shipping(weight)
    dead_code()
  src/vallm/cli/batch_processor_filter.py:
    e: parse_filter_patterns,should_exclude_file,matches_include_pattern
    parse_filter_patterns(include;exclude)
    should_exclude_file(file_path;compiled)
    matches_include_pattern(file_path;compiled)
  src/vallm/cli/output_formatters/batch.py:
    e: output_batch_results,output_batch_empty,_toon_row,_split_toon_results,_ordered_unsupported_items,_unsupported_bucket,_build_unsupported_summary,_print_toon_file_section,_print_toon_unsupported_section,output_batch_rich,output_batch_text,output_batch_json,output_batch_yaml,output_batch_toon,print_summary_header,build_results_table
    output_batch_results(results_by_language;filtered_files;passed_count;failed_files;output_format)
    output_batch_empty(output_format)
    _toon_row(values)
    _split_toon_results(files_details)
    _ordered_unsupported_items(unsupported_counts)
    _unsupported_bucket(file_path)
    _build_unsupported_summary(failed_files)
    _print_toon_file_section(title;files)
    _print_toon_unsupported_section(unsupported_counts)
    output_batch_rich(results_by_language;filtered_files;passed_count;failed_files)
    output_batch_text(results_by_language;filtered_files;passed_count;failed_files)
    output_batch_json(results_by_language;filtered_files;passed_count;failed_files)
    output_batch_yaml(results_by_language;filtered_files;passed_count;failed_files)
    output_batch_toon(results_by_language;filtered_files;passed_count;failed_files)
    print_summary_header()
    build_results_table(results_by_language)
  examples/04_graph_analysis/main.py:
    e: main
    main()
  examples/12_ollama_simple_demo/utils/process_user_input.py:
    e: process_user_input
    process_user_input(user_input)
  examples/12_ollama_simple_demo/ollama_simple_demo.py:
    e: Colors,log_section,log_step,analyze_with_code2llm,call_ollama,validate_with_vallm,run_simple_test,generate_ollama_prompt,run_simple_workflow,main
    Colors:
    log_section(title)
    log_step(step;description)
    analyze_with_code2llm(code_path)
    call_ollama(prompt;model)
    validate_with_vallm(code)
    run_simple_test(code)
    generate_ollama_prompt(code;analysis)
    run_simple_workflow(code_path;max_iterations)
    main()
  examples/10_mcp_ollama_demo/refactored_output.py:
    e: OrderManager,validate_email,calculate_shipping,load_config,save_data,process_order,main
    OrderManager: __init__(0),add_order(1),validate_order(1),execute_query(1),process_payment(2),send_email(3),get_stats(0)  # Class with single responsibility - adheres to SOLID principl...
    validate_email(email)
    calculate_shipping(weight)
    load_config()
    save_data(data;filename)
    process_order(data)
    main()
  src/vallm/validators/security.py:
    e: SecurityValidator
    SecurityValidator(BaseValidator): validate(2),_check_patterns(2),_check_python_ast(1),_get_func_name(0),_try_bandit(0)  # Tier 2: Security analysis using built-in patterns and option...
  src/vallm/validators/lint.py:
    e: LintValidator,create_validator
    LintValidator: __init__(1),validate(2),_check_ruff(1),_parse_ruff_result(1),_parse_ruff_text(1)  # Validator for linting issues using ruff...
    create_validator(settings)
  src/vallm/core/graph_diff.py:
    e: GraphDiffResult,diff_graphs,diff_python_code,_diff_list
    GraphDiffResult:  # Result of comparing two code graphs...
    diff_graphs(before;after)
    diff_python_code(before_code;after_code)
    _diff_list(before;after;added)
  src/vallm/cli/batch_processor_files.py:
    e: build_file_list
    build_file_list(paths;recursive)
  backend/routers/tickets/webhook.py:
    e: handle_pr_webhook,bulk_close_tickets,bulk_reprocess_tickets
    handle_pr_webhook(payload;db)
    bulk_close_tickets(ticket_ids;user;db)
    bulk_reprocess_tickets(ticket_ids;user;db)
  examples/15_cli_usage/main.py:
    e: run_cli_command,demo_single_file_validation,demo_batch_validation,demo_output_formats,demo_programmatic_cli,demo_check_command,main
    run_cli_command(cmd)
    demo_single_file_validation()
    demo_batch_validation()
    demo_output_formats()
    demo_programmatic_cli()
    demo_check_command()
    main()
  examples/12_ollama_simple_demo/legacy_code/simple_buggy.py:
    e: BadClass,process_user_input,load_config,save_data,calculate_total,duplicate_function,duplicate_function,unused_function,main
    BadClass: __init__(0),process_data(1),another_method(0)  # Class with multiple issues...
    process_user_input(user_input)
    load_config()
    save_data(data;filename)
    calculate_total(items)
    duplicate_function()
    duplicate_function()
    unused_function()
    main()
  examples/08_code2llm_integration/main.py:
    e: create_sample_project,analyze_with_code2llm,validate_with_vallm,generate_report,main
    create_sample_project(base_path)
    analyze_with_code2llm(project_path)
    validate_with_vallm(project_path)
    generate_report(code2llm_result;vallm_result;output_path)
    main()
  src/vallm/cli/batch_processor_patterns.py:
    e: _CompiledPatterns,_compile_patterns,parse_filter_patterns,matches_pattern,should_exclude_file,matches_include_pattern,filter_files
    _CompiledPatterns: __init__(3)  # Pre-compiled pattern set: exact names in a frozenset, globs ...
    _compile_patterns(raw)
    parse_filter_patterns(include;exclude)
    matches_pattern(path;compiled)
    should_exclude_file(path;exclude_patterns)
    matches_include_pattern(path;include_patterns)
    filter_files(files;include;exclude;gitignore_parser;use_gitignore;console)
  src/vallm/cli/output_formatters/shared.py:
    e: format_error_message,build_files_data,build_failed_files_data,_toon_today
    format_error_message(error)
    build_files_data(results_by_language)
    build_failed_files_data(failed_files)
    _toon_today()
  src/vallm/cli/command_handlers.py:
    e: validate_command,check_command,batch_command,info_command,_load_code,_load_reference,_detect_and_log_language,_build_proposal,_exit_on_verdict,_show_language_info,_show_general_info
    validate_command(code;file;language;reference;config;enable_semantic;enable_security;enable_regression;model;output_format;verbose;exit_on_verdict)
    check_command(code;file;language;output_format)
    batch_command(paths;recursive;include;exclude;no_gitignore;enable_semantic;enable_security;enable_regression;no_imports;no_complexity;model;format_;output;fail_fast;verbose;show_issues)
    info_command(language;clear_cache)
    _load_code(file;code)
    _load_reference(reference)
    _detect_and_log_language(file;language)
    _build_proposal(code_str;detected_language;ref_code;file)
    _exit_on_verdict(result)
    _show_language_info(language)
    _show_general_info()
  examples/utils/extraction.py:
    e: extract_code_from_response,extract_json_from_response
    extract_code_from_response(response;language)
    extract_json_from_response(response)
  examples/14_api_advanced/main.py:
    e: demo_proposal_creation,demo_settings_customization,demo_result_interpretation,demo_workflow_integration,main
    demo_proposal_creation()
    demo_settings_customization()
    demo_result_interpretation()
    demo_workflow_integration()
    main()
  src/vallm/validators/regression.py:
    e: RegressionValidator
    RegressionValidator(BaseValidator): __init__(3),validate(2),_resolve_test_dir(1),_write_code(2),_build_pytest_cmd(2),_run_pytest(3),_interpret(1),_parse_failures(1),_timeout_result(0),_exception_result(1)  # Tier 2: Run pytest against proposed code and report pass/fai...
  src/vallm/validators/imports/java_imports.py:
    e: JavaImportValidator
    JavaImportValidator(BaseImportValidator): get_language(0),_get_error_message(1),_get_rule_name(0),extract_imports(1),module_exists(1)  # Java import validator...
  src/vallm/scoring.py:
    e: Verdict,Severity,Issue,ValidationResult,PipelineResult,compute_verdict,validate,_initialize_settings,_initialize_context,_initialize_validators,_run_validation_pipeline,_get_default_validators
    Verdict(Enum):
    Severity(Enum):
    Issue: __str__(0)  # A single issue found during validation...
    ValidationResult:  # Result from a single validator...
    PipelineResult:  # Aggregated result from all validators...
    compute_verdict(results;settings;filename)
    validate(proposal;settings;validators;context)
    _initialize_settings(settings)
    _initialize_context(context)
    _initialize_validators(validators;settings)
    _run_validation_pipeline(proposal;validators;context;settings)
    _get_default_validators(settings)
  src/vallm/cli/batch_processor_validation.py:
    e: validate_single_file,process_files
    validate_single_file(file_path;settings)
    process_files(files;settings;output_format;fail_fast;verbose;show_issues)
  backend/routers/tickets/crud.py:
    e: create_new_ticket,list_tickets,get_stats,search_tickets_endpoint,get_tickets_for_repo,get_action_required_tickets,get_single_ticket,update_existing_ticket,delete_existing_ticket
    create_new_ticket(data;user;db)
    list_tickets(status;user;db)
    get_stats(user;db)
    search_tickets_endpoint(q;user;db)
    get_tickets_for_repo(repo;user;db)
    get_action_required_tickets(user;db)
    get_single_ticket(ticket_id;user;db)
    update_existing_ticket(ticket_id;data;user;db)
    delete_existing_ticket(ticket_id;user;db)
  examples/16_configuration/main.py:
    e: demo_config_file,demo_environment_variables,demo_runtime_configuration,demo_profile_switching,demo_threshold_configuration,main
    demo_config_file()
    demo_environment_variables()
    demo_runtime_configuration()
    demo_profile_switching()
    demo_threshold_configuration()
    main()
  src/vallm/validators/logical.py:
    e: LogicalErrorValidator,create_validator
    LogicalErrorValidator: __init__(1),validate(2),_check_pyflakes(1),_parse_pyflakes_line(1)  # Validator for logical errors using pyflakes...
    create_validator(settings)
  src/vallm/cli/batch_utils.py:
    e: CompiledPatterns,compile_patterns
    CompiledPatterns(NamedTuple):
    compile_patterns(raw)
  src/vallm/core/languages.py:
    e: Language,detect_language,get_language_for_validation
    Language(Enum): __init__(3),from_extension(1),from_path(1),from_string(1)  # Supported programming languages with their tree-sitter ident...
    detect_language(source)
    get_language_for_validation(source;explicit)
  src/vallm/cli/output_formatters/single.py:
    e: output_json,output_text,output_rich
    output_json(result)
    output_text(result)
    output_rich(result;verbose)
  mcp/server/self_server.py:
    e: handle_initialize,handle_tools_list,handle_tools_call,handle_request,main
    handle_initialize(request_id)
    handle_tools_list(request_id)
    handle_tools_call(request_id;params)
    handle_request(request)
    main()
  examples/03_security_check/main.py:
    e: main
    main()
  src/vallm/validators/semantic_cache.py:
    e: SemanticCache,get_semantic_cache,clear_semantic_cache
    SemanticCache: __init__(1),_get_cache_key(3),get(3),set(4),clear(0),get_cache_stats(0)  # Cache for semantic validation results to improve performance...
    get_semantic_cache()
    clear_semantic_cache()
  src/vallm/validators/semantic.py:
    e: SemanticValidator
    SemanticValidator(BaseValidator): __init__(1),validate(2),_build_prompt(1),_call_llm(1),_call_ollama(1),_call_litellm(1),_call_http(1),_parse_response(1),_extract_json_from_response(1),_create_parse_error_result(1),_create_json_error_result(1),_parse_scores(1),_parse_issues(1),_parse_severity(1),_parse_line_number(1)  # Tier 3: LLM-as-judge semantic code review...
  src/vallm/validators/imports/javascript_imports.py:
    e: JavaScriptImportValidator
    JavaScriptImportValidator(BaseImportValidator): __init__(1),validate(2),extract_imports(1),module_exists(1),get_language(0),_get_error_message(1),_get_rule_name(0)  # JavaScript/TypeScript import validator...
  src/vallm/validators/imports/go_imports.py:
    e: GoImportValidator
    GoImportValidator(BaseImportValidator): get_language(0),_get_error_message(1),_get_rule_name(0),extract_imports(1),module_exists(1)  # Go import validator...
  src/vallm/validators/imports/c_imports.py:
    e: CImportValidator
    CImportValidator(BaseImportValidator): __init__(1),validate(2),extract_imports(1),module_exists(1)  # C/C++ import validator...
  scripts/bump_version.py:
    e: bump_version,main
    bump_version(version_str;bump_type)
    main()
  frontend/e2e/loginTestHelpers.js:
    e: FRONTEND_URL,MOCK_GITHUB_URL,attemptLogin,element,attemptUserLogin,element,checkLoginStatus,testOAuthFlow,loginClicked,userButtonClicked,isLoggedIn
    FRONTEND_URL()
    MOCK_GITHUB_URL()
    attemptLogin()
    element()
    attemptUserLogin()
    element()
    checkLoginStatus()
    testOAuthFlow()
    loginClicked()
    userButtonClicked()
    isLoggedIn()
  examples/06_multilang_validation/main.py:
    e: main
    main()
  src/vallm/validators/syntax.py:
    e: SyntaxValidator
    SyntaxValidator(BaseValidator): validate(2),_validate_python(1),_validate_treesitter(2)  # Tier 1: Fast syntax validation...
  src/vallm/core/ast_compare.py:
    e: _cached_get_parser,parse_code,parse_python_ast,normalize_python_ast,python_ast_similarity,tree_sitter_node_count,tree_sitter_error_count,structural_diff_summary
    _cached_get_parser(language)
    parse_code(code;language)
    parse_python_ast(code)
    normalize_python_ast(tree)
    python_ast_similarity(code1;code2)
    tree_sitter_node_count(code;language)
    tree_sitter_error_count(code;language)
    structural_diff_summary(code1;code2;language)
  src/vallm/cli/output_formatters/base.py:
    e: output_validate_result,output_batch_results
    output_validate_result(result;output_format;verbose)
    output_batch_results(results_by_language;filtered_files;passed_count;failed_files;output_format)
  src/vallm/cli/output_formatters/__init__.py:
    e: _toon_today,output_validate_result,output_batch_results
    _toon_today()
    output_validate_result(result;output_format;verbose)
    output_batch_results(results_by_language;filtered_files;passed_count;failed_files;output_format)
  src/vallm/sandbox/runner.py:
    e: ExecutionResult,SandboxRunner
    ExecutionResult:  # Result of sandboxed code execution...
    SandboxRunner: __init__(1),run(2),_run_subprocess(2),_run_docker(2)  # Unified interface for running code in a sandbox...
  backend/routers/tickets/models.py:
    e: TicketCreate,TicketUpdate,TicketResponse,TicketListResponse,TicketStatsResponse,RedslAutoPRRequest,RedslAutoPRResponse,_get_tenant_for_user
    TicketCreate(BaseModel):
    TicketUpdate(BaseModel):
    TicketResponse(BaseModel):
    TicketListResponse(BaseModel):
    TicketStatsResponse(BaseModel):
    RedslAutoPRRequest(BaseModel):
    RedslAutoPRResponse(BaseModel):
    _get_tenant_for_user(user;db)
  frontend/e2e/gui-login-enhanced.spec.js:
    i: ./loginTestHelpers,@playwright/test
    e: res,result,result,result,loginElement,content,currentUrl,isLoggedIn
    res()
    result()
    result()
    result()
    loginElement()
    content()
    currentUrl()
    isLoggedIn()
  examples/12_ollama_simple_demo/utils/calculate_total.py:
    e: calculate_total
    calculate_total(items)
  examples/mcp_demo.py:
    e: example_syntax_validation,example_security_validation,example_full_pipeline,example_selective_validation,main
    example_syntax_validation()
    example_security_validation()
    example_full_pipeline()
    example_selective_validation()
    main()
  examples/utils/extract_code_from_response.py:
    e: extract_code_from_response
    extract_code_from_response(response)
  src/vallm/validators/file_cache.py:
    e: FileValidationCache,get_file_cache,clear_file_cache
    FileValidationCache: __init__(0),_key(0),get(1),set(2),clear(0)  # In-memory cache keyed on file path + mtime + size...
    get_file_cache()
    clear_file_cache()
  src/vallm/validators/imports/base.py:
    e: BaseImportValidator
    BaseImportValidator(ABC): validate(2),extract_imports(1),module_exists(1),get_language(0),_get_error_message(1),_get_rule_name(0),create_validation_result(4)  # Base class for all import validators...
  src/vallm/validators/imports/rust_imports.py:
    e: RustImportValidator
    RustImportValidator(BaseImportValidator): get_language(0),_get_error_message(1),_get_rule_name(0),extract_imports(1),module_exists(1)  # Rust import validator...
  src/vallm/cli/output_formatters/utils.py:
    e: format_error_message,build_files_data,build_failed_files_data
    format_error_message(error)
    build_files_data(results_by_language)
    build_failed_files_data(failed_files)
  src/vallm/config.py:
    e: VallmSettings,get_settings,reload_settings,get_default_filenames,get_default_output_format,get_default_language
    VallmSettings(BaseSettings): from_toml(1)  # vallm configuration with layered sources: defaults → TOML → ...
    get_settings()
    reload_settings()
    get_default_filenames()
    get_default_output_format()
    get_default_language()
  examples/05_llm_semantic_review/main_template.py:
    e: main
    main()
  examples/01_basic_validation/main.py:
    e: main
    main()
  examples/06_multilang_validation/main_template.py:
    e: main
    main()
  examples/02_ast_comparison/main.py:
    e: main
    main()
  examples/utils/logging_utils.py:
    e: Colors,log_section,log_step,log_code,log_result
    Colors:  # ANSI color codes for terminal output...
    log_section(title)
    log_step(step;description)
    log_code(label;code;max_lines)
    log_result(status;message)
  src/vallm/validators/imports/wrapper.py:
    e: ImportValidator
    ImportValidator(BaseValidator): validate(2)  # Backward compatibility wrapper for the refactored import val...
  src/vallm/validators/imports/factory.py:
    e: ImportValidatorFactory
    ImportValidatorFactory: create_validator(1),supported_languages(0),register_validator(2)  # Factory for creating language-specific import validators...
  examples/12_ollama_simple_demo/iteration_1.py:
    e: main
    main()
  examples/12_ollama_simple_demo/best_version.py:
    e: main
    main()
  examples/12_ollama_simple_demo/iteration_2.py:
    e: main
    main()
  examples/12_ollama_simple_demo/utils/load_config.py:
    e: load_config
    load_config()
  examples/12_ollama_simple_demo/utils/main.py:
    e: run_demo_main
    run_demo_main()
  examples/12_ollama_simple_demo/utils/save_data.py:
    e: save_data
    save_data(data;filename)
  examples/utils/save_analysis_data.py:
    e: save_analysis_data
    save_analysis_data(example_name;result_data)
  src/vallm/hookspecs.py:
    e: VallmSpec
    VallmSpec: validate_proposal(2),get_validator_name(0),get_validator_tier(0)  # Hook specifications that validators must implement...
  src/vallm/validators/base.py:
    e: BaseValidator
    BaseValidator(ABC): validate(2)  # Base class for all vallm validators...
  project.sh:
  mcp_server.py:
  backend/routers/tickets/__init__.py:
  examples/run.sh:
    e: run_example
    run_example()
  examples/__init__.py:
  examples/cycle-test/full-cycle.sh:
    e: semcod,print
    semcod()
    print()
  examples/cycle-test/validate-steps.sh:
    e: check,semcod
    check()
    semcod()
  examples/11_claude_code_autonomous/run.sh:
    e: print_section,print_step,print_success,print_warning,print_error
    print_section()
    print_step()
    print_success()
    print_warning()
    print_error()
  examples/11_claude_code_autonomous/docker-entrypoint.sh:
  examples/12_ollama_simple_demo/run.sh:
  examples/12_ollama_simple_demo/docker-entrypoint.sh:
  examples/12_ollama_simple_demo/utils/__init__.py:
  examples/10_mcp_ollama_demo/docker-entrypoint.sh:
  examples/10_mcp_ollama_demo/run.sh:
    e: print_section,print_step,print_success,print_warning,print_error,print,print,print,print
    print_section()
    print_step()
    print_success()
    print_warning()
    print_error()
    print()
    print()
    print()
    print()
  src/vallm/cli/__init__.py:
  src/vallm/__init__.py:
  src/vallm/__main__.py:
  src/vallm/validators/__init__.py:
  src/vallm/validators/imports/__init__.py:
  src/vallm/core/__init__.py:
  src/vallm/core/proposal.py:
    e: Proposal
    Proposal:  # A code proposal to be validated.

Attributes:
    code: The ...
  src/vallm/cli/batch_constants.py:
  src/vallm/cli/batch_processor.py:
  src/vallm/sandbox/__init__.py:
  scripts/test_docker_installation.sh:
    e: print_status,print_warning,print_error,test_image
    print_status()
    print_warning()
    print_error()
    test_image()
  mcp/__init__.py:
  mcp/server/__init__.py:
```

## Intent

A complete toolkit for validating LLM-generated code
