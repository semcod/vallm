# vallm

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `vallm`
- **version**: `0.1.74`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, app.doql.css, pyqual.yaml, goal.yaml, .env.example, project/(5 analysis files)

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 68f 7626L | python:62,javascript:4,shell:2 | 2026-04-19
# CC̄=3.4 | critical:1/480 | dups:0 | cycles:0

HEALTH[2]:
  🟡 CC    RedslHealthCard CC=15 (limit:15)
  🟡 CC    main CC=16 (limit:15)

REFACTOR[1]:
  1. split 2 high-CC methods  (CC>15)

PIPELINES[230]:
  [1] Src [process_ticket_with_redsl]: process_ticket_with_redsl → _get_tenant_for_user
      PURITY: 100% pure
  [2] Src [_create_pr_for_ticket]: _create_pr_for_ticket
      PURITY: 100% pure
  [3] Src [get_ticket_processing_status]: get_ticket_processing_status → _get_tenant_for_user
      PURITY: 100% pure
  [4] Src [handle_pr_webhook]: handle_pr_webhook
      PURITY: 100% pure
  [5] Src [bulk_close_tickets]: bulk_close_tickets → _get_tenant_for_user
      PURITY: 100% pure

LAYERS:
  backend/                        CC̄=4.1    ←in:0  →out:0
  │ redsl                      243L  0C    3m  CC=14     ←0
  │ crud                       187L  0C    9m  CC=6      ←0
  │ models                      96L  7C    1m  CC=4      ←3
  │ webhook                     92L  0C    3m  CC=8      ←0
  │ __init__                    19L  0C    0m  CC=0.0    ←0
  │
  src/                            CC̄=3.4    ←in:0  →out:0
  │ batch_processor_impl       487L  1C   22m  CC=13     ←0
  │ command_handlers           345L  0C   11m  CC=8      ←0
  │ batch                      315L  0C   16m  CC=10     ←2
  │ semantic                   302L  1C   15m  CC=5      ←0
  │ gitignore                  272L  1C   10m  CC=11     ←1
  │ regression                 265L  1C   10m  CC=7      ←0
  │ security                   255L  1C    5m  CC=9      ←0
  │ languages                  227L  1C    6m  CC=6      ←6
  │ python_imports             225L  1C    9m  CC=14     ←0
  │ scoring                    218L  5C    8m  CC=7      ←0
  │ semantic_cache             187L  1C    8m  CC=5      ←2
  │ complexity                 183L  1C    4m  CC=12     ←16
  │ lint                       182L  1C    6m  CC=9      ←0
  │ utils                      166L  0C    5m  CC=14     ←5
  │ runner                     144L  2C    4m  CC=4      ←0
  │ logical                    142L  1C    5m  CC=6      ←0
  │ ast_compare                142L  0C    8m  CC=4      ←5
  │ batch_processor_patterns   126L  1C    7m  CC=8      ←2
  │ config                     122L  1C    6m  CC=3      ←1
  │ javascript_imports         118L  1C    7m  CC=5      ←0
  │ graph_diff                 104L  1C    3m  CC=9      ←1
  │ syntax                      96L  1C    3m  CC=4      ←0
  │ c_imports                   88L  1C    4m  CC=5      ←0
  │ go_imports                  84L  1C    5m  CC=5      ←0
  │ file_cache                  82L  1C    7m  CC=3      ←7
  │ single                      80L  0C    3m  CC=6      ←2
  │ __init__                    79L  0C    3m  CC=4      ←1
  │ rust_imports                78L  1C    5m  CC=3      ←0
  │ batch_processor_validation    78L  0C    2m  CC=7      ←0
  │ base                        70L  1C    7m  CC=3      ←0
  │ java_imports                68L  1C    5m  CC=7      ←0
  │ shared                      63L  0C    4m  CC=8      ←1
  │ __init__                    45L  0C    0m  CC=0.0    ←0
  │ factory                     43L  1C    3m  CC=2      ←1
  │ proposal                    37L  1C    0m  CC=0.0    ←0
  │ hookspecs                   33L  1C    3m  CC=1      ←0
  │ wrapper                     30L  1C    1m  CC=2      ←0
  │ batch_processor_files       25L  0C    1m  CC=9      ←1
  │ batch_processor_filter      25L  0C    3m  CC=10     ←0
  │ __init__                    25L  0C    0m  CC=0.0    ←0
  │ batch_constants             23L  0C    0m  CC=0.0    ←0
  │ batch_utils                 22L  1C    1m  CC=6      ←0
  │ base                        21L  1C    1m  CC=1      ←0
  │ base                        19L  0C    2m  CC=4      ←1
  │ __init__                    19L  0C    0m  CC=0.0    ←0
  │ utils                       11L  0C    3m  CC=3      ←0
  │ __main__                     5L  0C    0m  CC=0.0    ←0
  │ batch_processor              5L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  mcp/                            CC̄=3.3    ←in:0  →out:0
  │ _tools_vallm               464L  0C   14m  CC=12     ←1
  │ self_server                185L  0C    5m  CC=6      ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  frontend/                       CC̄=3.2    ←in:0  →out:0
  │ loginTestHelpers.js         98L  0C   10m  CC=4      ←0
  │ RedslHealthCard.parts.jsx    95L  0C    9m  CC=14     ←0
  │ gui-login-enhanced.spec.js    61L  0C    6m  CC=3      ←0
  │ !! RedslHealthCard.jsx         49L  0C    4m  CC=15     ←0
  │
  scripts/                        CC̄=1.7    ←in:0  →out:0
  │ test_docker_installation.sh   106L  0C    4m  CC=0.0    ←0
  │ bump_version                78L  0C    2m  CC=5      ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ project.sh                  37L  0C    0m  CC=0.0    ←0
  │ mcp_server                  28L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 17 groups | 104f 12836L | 2026-04-19

SUMMARY:
  files_scanned: 104
  total_lines:   12836
  dup_groups:    17
  dup_fragments: 44
  saved_lines:   183
  scan_ms:       5497

HOTSPOTS[7] (files with most duplication):
  mcp/server/_tools_vallm.py  dup=100L  groups=2  frags=6  (0.8%)
  examples/10_mcp_ollama_demo/legacy_code/order_processor.py  dup=20L  groups=3  frags=4  (0.2%)
  backend/routers/tickets/crud.py  dup=18L  groups=1  frags=2  (0.1%)
  src/vallm/cli/output_formatters/__init__.py  dup=16L  groups=1  frags=1  (0.1%)
  src/vallm/cli/output_formatters/batch.py  dup=16L  groups=1  frags=1  (0.1%)
  examples/05_llm_semantic_review/main_template.py  dup=14L  groups=1  frags=1  (0.1%)
  examples/06_multilang_validation/main_template.py  dup=14L  groups=1  frags=1  (0.1%)

DUPLICATES[17] (ranked by impact):
  [1e916868fd12c434] ! STRU  validate_syntax  L=26 N=3 saved=52 sim=1.00
      mcp/server/_tools_vallm.py:154-179  (validate_syntax)
      mcp/server/_tools_vallm.py:182-207  (validate_imports)
      mcp/server/_tools_vallm.py:210-236  (validate_security)
  [0377ac5715a548c6]   EXAC  output_batch_results  L=16 N=2 saved=16 sim=1.00
      src/vallm/cli/output_formatters/__init__.py:39-54  (output_batch_results)
      src/vallm/cli/output_formatters/batch.py:27-42  (output_batch_results)
  [6baf28048162b351]   STRU  main  L=14 N=2 saved=14 sim=1.00
      examples/05_llm_semantic_review/main_template.py:57-70  (main)
      examples/06_multilang_validation/main_template.py:57-70  (main)
  [68b30236533a58ae]   STRU  handle_validate_syntax  L=7 N=3 saved=14 sim=1.00
      mcp/server/_tools_vallm.py:291-297  (handle_validate_syntax)
      mcp/server/_tools_vallm.py:300-306  (handle_validate_imports)
      mcp/server/_tools_vallm.py:309-315  (handle_validate_security)
  [27dda1031a29e18a]   EXAC  load_config  L=5 N=3 saved=10 sim=1.00
      examples/10_mcp_ollama_demo/legacy_code/order_processor.py:34-38  (load_config)
      examples/11_claude_code_autonomous/legacy_code/data_processor.py:19-22  (load_config)
      examples/12_ollama_simple_demo/legacy_code/simple_buggy.py:29-32  (load_config)
  [2a8f79ba6c631f6f]   STRU  create_validator  L=10 N=2 saved=10 sim=1.00
      src/vallm/validators/lint.py:173-182  (create_validator)
      src/vallm/validators/logical.py:133-142  (create_validator)
  [0ee70ff9b8d9f87e]   STRU  search_tickets_endpoint  L=9 N=2 saved=9 sim=1.00
      backend/routers/tickets/crud.py:89-97  (search_tickets_endpoint)
      backend/routers/tickets/crud.py:101-109  (get_tickets_for_repo)
  [7c6fc4484a4bfb49]   STRU  _get_error_message  L=3 N=4 saved=9 sim=1.00
      src/vallm/validators/imports/go_imports.py:26-28  (_get_error_message)
      src/vallm/validators/imports/java_imports.py:25-27  (_get_error_message)
      src/vallm/validators/imports/javascript_imports.py:112-114  (_get_error_message)
      src/vallm/validators/imports/rust_imports.py:25-27  (_get_error_message)
  [d96fbe45dd774d8b]   STRU  _get_rule_name  L=3 N=4 saved=9 sim=1.00
      src/vallm/validators/imports/go_imports.py:30-32  (_get_rule_name)
      src/vallm/validators/imports/java_imports.py:29-31  (_get_rule_name)
      src/vallm/validators/imports/javascript_imports.py:116-118  (_get_rule_name)
      src/vallm/validators/imports/rust_imports.py:29-31  (_get_rule_name)
  [de3da32194b04163]   EXAC  log_step  L=4 N=3 saved=8 sim=1.00
      examples/10_mcp_ollama_demo/mcp_demo.py:53-56  (log_step)
      examples/11_claude_code_autonomous/claude_autonomous_demo.py:70-73  (log_step)
      examples/12_ollama_simple_demo/ollama_simple_demo.py:46-48  (log_step)
  [bf795f20b1fc2037]   EXAC  main  L=4 N=3 saved=8 sim=1.00
      examples/12_ollama_simple_demo/best_version.py:16-19  (main)
      examples/12_ollama_simple_demo/iteration_1.py:16-19  (main)
      examples/12_ollama_simple_demo/iteration_2.py:16-19  (main)
  [b1da8e8f33b7f775]   STRU  validate_email_1  L=6 N=2 saved=6 sim=1.00
      examples/10_mcp_ollama_demo/legacy_code/order_processor.py:102-107  (validate_email_1)
      examples/10_mcp_ollama_demo/legacy_code/order_processor.py:109-114  (validate_email_2)
  [29507c36c8dbf2ce]   STRU  get_language  L=3 N=3 saved=6 sim=1.00
      src/vallm/validators/imports/go_imports.py:22-24  (get_language)
      src/vallm/validators/imports/java_imports.py:21-23  (get_language)
      src/vallm/validators/imports/rust_imports.py:21-23  (get_language)
  [bd60d2849a7474ac]   EXAC  __init__  L=3 N=2 saved=3 sim=1.00
      src/vallm/validators/lint.py:21-23  (__init__)
      src/vallm/validators/logical.py:20-22  (__init__)
  [aaae754bdb04529d]   STRU  dead_code  L=3 N=2 saved=3 sim=1.00
      examples/10_mcp_ollama_demo/legacy_code/order_processor.py:129-131  (dead_code)
      examples/12_ollama_simple_demo/legacy_code/simple_buggy.py:60-62  (unused_function)
  [a1c06b6eb8eec00e]   STRU  duplicate_function  L=3 N=2 saved=3 sim=1.00
      examples/12_ollama_simple_demo/legacy_code/simple_buggy.py:52-54  (duplicate_function)
      examples/12_ollama_simple_demo/legacy_code/simple_buggy.py:56-58  (duplicate_function)
  [ab5b16619a4fdd19]   STRU  get_default_output_format  L=3 N=2 saved=3 sim=1.00
      src/vallm/config.py:115-117  (get_default_output_format)
      src/vallm/config.py:120-122  (get_default_language)

REFACTOR[17] (ranked by priority):
  [1] ○ extract_function   → mcp/server/utils/validate_syntax.py
      WHY: 3 occurrences of 26-line block across 1 files — saves 52 lines
      FILES: mcp/server/_tools_vallm.py
  [2] ○ extract_function   → src/vallm/cli/output_formatters/utils/output_batch_results.py
      WHY: 2 occurrences of 16-line block across 2 files — saves 16 lines
      FILES: src/vallm/cli/output_formatters/__init__.py, src/vallm/cli/output_formatters/batch.py
  [3] ○ extract_function   → examples/utils/main.py
      WHY: 2 occurrences of 14-line block across 2 files — saves 14 lines
      FILES: examples/05_llm_semantic_review/main_template.py, examples/06_multilang_validation/main_template.py
  [4] ○ extract_function   → mcp/server/utils/handle_validate_syntax.py
      WHY: 3 occurrences of 7-line block across 1 files — saves 14 lines
      FILES: mcp/server/_tools_vallm.py
  [5] ○ extract_function   → examples/utils/load_config.py
      WHY: 3 occurrences of 5-line block across 3 files — saves 10 lines
      FILES: examples/10_mcp_ollama_demo/legacy_code/order_processor.py, examples/11_claude_code_autonomous/legacy_code/data_processor.py, examples/12_ollama_simple_demo/legacy_code/simple_buggy.py
  [6] ○ extract_function   → src/vallm/validators/utils/create_validator.py
      WHY: 2 occurrences of 10-line block across 2 files — saves 10 lines
      FILES: src/vallm/validators/lint.py, src/vallm/validators/logical.py
  [7] ○ extract_function   → backend/routers/tickets/utils/search_tickets_endpoint.py
      WHY: 2 occurrences of 9-line block across 1 files — saves 9 lines
      FILES: backend/routers/tickets/crud.py
  [8] ○ extract_function   → src/vallm/validators/imports/utils/_get_error_message.py
      WHY: 4 occurrences of 3-line block across 4 files — saves 9 lines
      FILES: src/vallm/validators/imports/go_imports.py, src/vallm/validators/imports/java_imports.py, src/vallm/validators/imports/javascript_imports.py, src/vallm/validators/imports/rust_imports.py
  [9] ○ extract_function   → src/vallm/validators/imports/utils/_get_rule_name.py
      WHY: 4 occurrences of 3-line block across 4 files — saves 9 lines
      FILES: src/vallm/validators/imports/go_imports.py, src/vallm/validators/imports/java_imports.py, src/vallm/validators/imports/javascript_imports.py, src/vallm/validators/imports/rust_imports.py
  [10] ○ extract_function   → examples/utils/log_step.py
      WHY: 3 occurrences of 4-line block across 3 files — saves 8 lines
      FILES: examples/10_mcp_ollama_demo/mcp_demo.py, examples/11_claude_code_autonomous/claude_autonomous_demo.py, examples/12_ollama_simple_demo/ollama_simple_demo.py
  [11] ○ extract_function   → examples/12_ollama_simple_demo/utils/main.py
      WHY: 3 occurrences of 4-line block across 3 files — saves 8 lines
      FILES: examples/12_ollama_simple_demo/best_version.py, examples/12_ollama_simple_demo/iteration_1.py, examples/12_ollama_simple_demo/iteration_2.py
  [12] ○ extract_function   → examples/10_mcp_ollama_demo/legacy_code/utils/validate_email_1.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: examples/10_mcp_ollama_demo/legacy_code/order_processor.py
  [13] ○ extract_function   → src/vallm/validators/imports/utils/get_language.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: src/vallm/validators/imports/go_imports.py, src/vallm/validators/imports/java_imports.py, src/vallm/validators/imports/rust_imports.py
  [14] ○ extract_function   → src/vallm/validators/utils/__init__.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/vallm/validators/lint.py, src/vallm/validators/logical.py
  [15] ○ extract_function   → examples/utils/dead_code.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: examples/10_mcp_ollama_demo/legacy_code/order_processor.py, examples/12_ollama_simple_demo/legacy_code/simple_buggy.py
  [16] ○ extract_function   → examples/12_ollama_simple_demo/legacy_code/utils/duplicate_function.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: examples/12_ollama_simple_demo/legacy_code/simple_buggy.py
  [17] ○ extract_function   → src/vallm/utils/get_default_output_format.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: src/vallm/config.py

QUICK_WINS[13] (low risk, high savings — do first):
  [1] extract_function   saved=52L  → mcp/server/utils/validate_syntax.py
      FILES: _tools_vallm.py
  [2] extract_function   saved=16L  → src/vallm/cli/output_formatters/utils/output_batch_results.py
      FILES: __init__.py, batch.py
  [3] extract_function   saved=14L  → examples/utils/main.py
      FILES: main_template.py, main_template.py
  [4] extract_function   saved=14L  → mcp/server/utils/handle_validate_syntax.py
      FILES: _tools_vallm.py
  [5] extract_function   saved=10L  → examples/utils/load_config.py
      FILES: order_processor.py, data_processor.py, simple_buggy.py
  [6] extract_function   saved=10L  → src/vallm/validators/utils/create_validator.py
      FILES: lint.py, logical.py
  [7] extract_function   saved=9L  → backend/routers/tickets/utils/search_tickets_endpoint.py
      FILES: crud.py
  [8] extract_function   saved=9L  → src/vallm/validators/imports/utils/_get_error_message.py
      FILES: go_imports.py, java_imports.py, javascript_imports.py +1
  [9] extract_function   saved=9L  → src/vallm/validators/imports/utils/_get_rule_name.py
      FILES: go_imports.py, java_imports.py, javascript_imports.py +1
  [10] extract_function   saved=8L  → examples/utils/log_step.py
      FILES: mcp_demo.py, claude_autonomous_demo.py, ollama_simple_demo.py

EFFORT_ESTIMATE (total ≈ 6.1h):
  hard   validate_syntax                     saved=52L  ~104min
  medium output_batch_results                saved=16L  ~32min
  easy   main                                saved=14L  ~28min
  easy   handle_validate_syntax              saved=14L  ~28min
  easy   load_config                         saved=10L  ~20min
  easy   create_validator                    saved=10L  ~20min
  easy   search_tickets_endpoint             saved=9L  ~18min
  easy   _get_error_message                  saved=9L  ~18min
  easy   _get_rule_name                      saved=9L  ~18min
  easy   log_step                            saved=8L  ~16min
  ... +7 more (~64min)

METRICS-TARGET:
  dup_groups:  17 → 0
  saved_lines: 183 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 305 func | 51f | 2026-04-19

NEXT[1] (ranked by impact):
  [1] !  SPLIT-FUNC      RedslHealthCard  CC=15  fan=13
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 195


RISKS[0]: none

METRICS-TARGET:
  CC̄:          3.4 → ≤2.4
  max-CC:      15 → ≤7
  god-modules: 0 → 0
  high-CC(≥15): 1 → ≤0
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=3.4 → now CC̄=3.4
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 204f | 131✓ 4⚠ 7✗ | 2026-04-19

SUMMARY:
  scanned: 204  passed: 131 (64.2%)  warnings: 4  errors: 7  unsupported: 64

WARNINGS[4]{path,score}:
  frontend/src/components/RedslHealthCard.jsx,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse jsx: Download error: Language 'jsx' not available for download. Available groups: [""all""]",
  frontend/src/components/RedslHealthCard.parts.jsx,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse jsx: Download error: Language 'jsx' not available for download. Available groups: [""all""]",
  examples/13_batch_processing/main.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.cyclomatic,warning,main has cyclomatic complexity 16 (max: 15),11
  src/vallm/cli/batch_processor_impl.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.maintainability,warning,Low maintainability index: 14.0 (threshold: 20),

ERRORS[7]{path,score}:
  project/evolution.yaml,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 1 parse error(s) in yaml,
  backend/routers/tickets/webhook.py,0.69
    issues[5]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,4
      python.import.resolvable,error,Module 'db_session' not found,6
      python.import.resolvable,error,Module 'db_module.tickets_orm' not found,7
      python.import.resolvable,error,Module 'routers.auth' not found,11
      python.import.resolvable,error,Module 'db_module.tickets_orm' not found,36
  backend/routers/tickets/crud.py,0.71
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,4
      python.import.resolvable,error,Module 'db_session' not found,6
      python.import.resolvable,error,Module 'db_module.tickets_orm' not found,7
      python.import.resolvable,error,Module 'routers.auth' not found,19
  backend/routers/tickets/redsl.py,0.71
    issues[6]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,5
      python.import.resolvable,error,Module 'db_session' not found,7
      python.import.resolvable,error,Module 'db_module.tickets_orm' not found,8
      python.import.resolvable,error,Module 'routers.auth' not found,14
      python.import.resolvable,error,Module 'services.redsl_client' not found,15
      python.import.resolvable,error,Module 'worker.tasks.autopr' not found,173
  src/vallm/cli/output_formatters/base.py,0.71
    issues[4]{rule,severity,message,line}:
      python.import.relative.resolvable,error,Relative import 'json_formatters' not found,2
      python.import.relative.resolvable,error,Relative import 'rich_formatters' not found,3
      python.import.relative.resolvable,error,Relative import 'text_formatters' not found,4
      python.import.relative.resolvable,error,Relative import 'toon_formatters' not found,5
  backend/routers/tickets/models.py,0.86
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'database' not found,6
  backend/routers/tickets/__init__.py,0.89
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,9

UNSUPPORTED[6]{bucket,count}:
  *.md,33
  Dockerfile*,4
  *.txt,12
  *.yml,1
  *.example,1
  other,13
```

## Intent

A complete toolkit for validating LLM-generated code
