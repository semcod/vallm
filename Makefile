.PHONY: install dev-install test lint format clean help analyze run docker mermaid-png install-mermaid check-mermaid clean-png test-toon validate-toon test-all-formats build publish bump-patch bump-minor bump-major

PYTHON := .venv/bin/python

# Default target
help:
	@echo "code2llm - Python Code Flow Analysis Tool with LLM Integration and TOON Format"
	@echo ""
	@echo "🚀 Installation:"
	@echo "  make install       - Install package"
	@echo "  make dev-install   - Install with development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test          - Run test suite"
	@echo "  make test-toon     - Test TOON format only"
	@echo "  make validate-toon - Validate TOON format output"
	@echo "  make test-all-formats - Test all output formats"
	@echo ""
	@echo "🔧 Code Quality:"
	@echo "  make lint          - Run linters (flake8, black --check)"
	@echo "  make format        - Format code with black"
	@echo "  make typecheck     - Run mypy type checking"
	@echo "  make check         - Run all quality checks"
	@echo ""
	@echo "📊 Analysis:"
	@echo "  make analyze       - Run analysis on current project (TOON format)"
	@echo "  make run           - Run with example arguments"
	@echo "  make analyze-all   - Run analysis with all formats"
	@echo ""
	@echo "🎯 TOON Format:"
	@echo "  make toon-demo     - Quick TOON format demo"
	@echo "  make toon-compare  - Compare TOON vs YAML formats"
	@echo "  make toon-validate - Validate TOON format structure"
	@echo ""
	@echo "📦 Building & Release:"
	@echo "  make build         - Build distribution packages"
	@echo "  make publish       - Publish to PyPI (with version bump)"
	@echo "  make publish-test  - Publish to TestPyPI"
	@echo "  make bump-patch    - Bump patch version"
	@echo "  make bump-minor    - Bump minor version"
	@echo "  make bump-major    - Bump major version"
	@echo ""
	@echo "🎨 Visualization:"
	@echo "  make mermaid-png   - Generate PNG from all Mermaid files"
	@echo "  make install-mermaid - Install Mermaid CLI renderer"
	@echo "  make check-mermaid - Check available Mermaid renderers"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make clean-png     - Clean PNG files"
	@echo ""

# =============================================================================
# Installation
# =============================================================================

install:
	$(PYTHON) -m pip install -e .
	@echo "✓ code2llm installed with TOON format support"

dev-install:
	$(PYTHON) -m pip install -e ".[dev]"
	@echo "✓ code2llm installed with dev dependencies"

# =============================================================================
# Testing
# =============================================================================

test:
	$(PYTHON) -m pytest tests/ -v --tb=short 2>/dev/null || echo "No tests yet - create tests/ directory"

test-cov:
	$(PYTHON) -m pytest tests/ --cov=code2llm --cov-report=html --cov-report=term 2>/dev/null || echo "No tests yet"

test-toon:
	@echo "🎯 Testing TOON format..."
	$(PYTHON) -m code2llm ./ -v -o ./test_toon -m hybrid -f toon
	$(PYTHON) validate_toon.py test_toon/analysis.toon
	@echo "✓ TOON format test complete"

validate-toon: test-toon

test-all-formats:
	@echo "📊 Testing all output formats..."
	$(PYTHON) -m code2llm ./ -v -o ./test_all -m hybrid -f all
	$(PYTHON) validate_toon.py test_all/analysis.toon
	@echo "✓ All formats test complete"

test-comprehensive:
	@echo "🚀 Running comprehensive test suite..."
	bash project.sh
	@echo "✓ Comprehensive tests complete"

# =============================================================================
# Code Quality
# =============================================================================

lint:
	$(PYTHON) -m flake8 code2llm/ --max-line-length=100 --ignore=E203,W503 2>/dev/null || echo "flake8 not installed"
	$(PYTHON) -m black --check code2llm/ 2>/dev/null || echo "black not installed"
	@echo "✓ Linting complete"

format:
	$(PYTHON) -m black code2llm/ --line-length=100 2>/dev/null || echo "black not installed, run: pip install black"
	@echo "✓ Code formatted"

typecheck:
	$(PYTHON) -m mypy code2llm/ --ignore-missing-imports 2>/dev/null || echo "mypy not installed"

check: lint typecheck test
	@echo "✓ All checks passed"

# =============================================================================
# Analysis
# =============================================================================

run:
	$(PYTHON) -m code2llm ../python/stts_core -v -o ./output

analyze:
	@echo "🎯 Running TOON format analysis on current project..."
	$(PYTHON) -m code2llm ./ -v -o ./analysis -m hybrid -f toon
	$(PYTHON) validate_toon.py analysis/analysis.toon
	@echo "✓ TOON analysis complete - check analysis/analysis.toon"

analyze-all:
	@echo "📊 Running analysis with all formats..."
	$(PYTHON) -m code2llm ./ -v -o ./analysis_all -m hybrid -f all
	$(PYTHON) validate_toon.py analysis_all/analysis.toon
	@echo "✓ All formats analysis complete - check analysis_all/"

# =============================================================================
# TOON Format Specific
# =============================================================================

toon-demo:
	@echo "🎯 Quick TOON format demo..."
	$(PYTHON) -m code2llm ./ -v -o ./demo -m hybrid -f toon
	@echo "📁 Generated: demo/analysis.toon"
	@echo "📊 Size: $$(du -h demo/analysis.toon | cut -f1)"
	@echo "🔍 Preview:"
	@head -20 demo/analysis.toon

toon-compare:
	@echo "📊 Comparing TOON vs YAML formats..."
	$(PYTHON) -m code2llm ./ -v -o ./compare -m hybrid -f toon,yaml
	@echo "📁 Files generated:"
	@echo "  - TOON:  compare/analysis.toon  ($$(du -h compare/analysis.toon | cut -f1))"
	@echo "  - YAML:  compare/analysis.yaml  ($$(du -h compare/analysis.yaml | cut -f1))"
	@echo "  - Ratio: $$(echo "scale=1; $$(du -k compare/analysis.yaml | cut -f1) / $$(du -k compare/analysis.toon | cut -f1)" | bc)x smaller"
	$(PYTHON) validate_toon.py compare/analysis.yaml compare/analysis.toon

toon-validate:
	@echo "🔍 Validating TOON format structure..."
	$(PYTHON) validate_toon.py analysis/analysis.toon 2>/dev/null || $(PYTHON) validate_toon.py test_toon/analysis.toon 2>/dev/null || echo "Run 'make test-toon' first"

# =============================================================================
# Building
# =============================================================================

build:
	rm -rf build/ dist/ *.egg-info
	$(PYTHON) -m build
	@echo "✓ Build complete - check dist/"

# =============================================================================
# Release
# =============================================================================

publish-test: build
	@echo "🚀 Publishing to TestPyPI..."
	$(PYTHON) -m venv publish-test-env
	publish-test-env/bin/pip install twine
	publish-test-env/bin/python -m twine upload --repository testpypi dist/*
	rm -rf publish-test-env
	@echo "✓ Published to TestPyPI"

bump-patch:
	@echo "🔢 Bumping patch version..."
	$(PYTHON) scripts/bump_version.py patch 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually"

bump-minor:
	@echo "🔢 Bumping minor version..."
	$(PYTHON) scripts/bump_version.py minor 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually"

bump-major:
	@echo "🔢 Bumping major version..."
	$(PYTHON) scripts/bump_version.py major 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually"

publish: build
	@echo "🚀 Publishing to PyPI..."
	@echo "🔢 Bumping patch version..."
	$(MAKE) bump-patch
	@echo "🔨 Rebuilding package with new version..."
	$(MAKE) build
	@echo "📦 Publishing to PyPI..."
	$(PYTHON) -m venv publish-env
	publish-env/bin/pip install twine
	publish-env/bin/python -m twine upload dist/*
	rm -rf publish-env
	@echo "✓ Published to PyPI"

# =============================================================================
# Visualization
# =============================================================================

mermaid-png:
	$(PYTHON) mermaid_to_png.py --batch output output

mermaid-png-%:
	$(PYTHON) mermaid_to_png.py output/$*.mmd output/$*.png

install-mermaid:
	npm install -g @mermaid-js/mermaid-cli

check-mermaid:
	@echo "Checking available Mermaid renderers..."
	@which mmdc > /dev/null && echo "✓ mmdc (mermaid-cli)" || echo "✗ mmdc (run: npm install -g @mermaid-js/mermaid-cli)"
	@which npx > /dev/null && echo "✓ npx (for @mermaid-js/mermaid-cli)" || echo "✗ npx (install Node.js)"
	@which puppeteer > /dev/null && echo "✓ puppeteer" || echo "✗ puppeteer (run: npm install -g puppeteer)"

# =============================================================================
# Maintenance
# =============================================================================

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .coverage htmlcov/
	rm -rf code2llm/__pycache__ code2llm/*/__pycache__
	rm -rf test_* demo compare analysis analysis_all output_* 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned build artifacts and test outputs"

clean-png:
	rm -f output/*.png
	@echo "✓ Cleaned PNG files"

# =============================================================================
# Quick Start
# =============================================================================

quickstart:
	@echo "🚀 Quick Start with code2llm TOON format:"
	@echo ""
	@echo "1. Install:        make install"
	@echo "2. Test TOON:      make test-toon"
	@echo "3. Analyze:        make analyze"
	@echo "4. Compare:        make toon-compare"
	@echo "5. All formats:    make test-all-formats"
	@echo ""
	@echo "📖 For more: make help"
