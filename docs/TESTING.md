---
path: /home/tom/github/semcod/vallm
---

# Comprehensive Testing Guide

This document describes the comprehensive testing suite for vallm, covering E2E tests, Docker installation tests, and CI/CD workflows.

### 1. E2E CLI Tests (`tests/test_cli_e2e.py`)
- **All CLI commands**: `validate`, `check`, `batch`, `info`
- **Options testing**: `--semantic`, `--security`, `--model`, `--verbose`
- **Batch validation**: recursive, include/exclude patterns, JSON/text output
- **Multi-language support**: Python, JavaScript, Go, Rust
- **Error handling**: missing files, syntax errors, invalid options
- **Configuration**: config files, environment variables

### 2. Installation Tests (`tests/test_installation.py`)
- **pip installation**: editable mode, wheel installation, with extras
- **pipx installation**: editable mode, with extras
- **Post-installation validation**: basic functionality, language detection
- **Virtual environment testing**: isolated installation testing

### 3. Semantic Validation Tests (`tests/test_semantic_validation.py`)
- **LLM integration**: mock providers, availability checks
- **Code quality assessment**: good code, bad code, syntax errors
- **Multi-language semantic analysis**: Python, JavaScript, Go, Rust
- **Reference code comparison**: diff-based analysis
- **Edge cases**: empty code, very long code, unsupported languages

### 4. Docker Installation Tests
- **Multi-system support**: Ubuntu 22.04/24.04, Debian 12, Alpine, Fedora 39, CentOS 9
- **Python images**: slim, Alpine variants
- **Post-installation validation**: help, info, basic validation
- **Cross-platform compatibility**: different package managers, Python versions

# Run specific test suites
pytest tests/test_cli_e2e.py -v
pytest tests/test_installation.py -v
pytest tests/test_semantic_validation.py -v

# Run with coverage
pytest tests/ --cov=vallm --cov-report=html

# Run performance tests
pytest tests/ --benchmark-only
```

# Test Docker installation across systems
./scripts/test_docker_installation.sh

# Test specific Docker stage
docker build --target ubuntu-22 -t vallm-test -f Dockerfile.test .
docker run --rm vallm-test vallm --help
```

### CI/CD Testing
The comprehensive GitHub Actions workflow includes:
- **Matrix testing**: multiple OS and Python versions
- **Docker testing**: multi-system installation
- **Integration testing**: LLM integration with Ollama
- **Performance testing**: large project validation
- **Security testing**: vulnerability scanning
- **Compatibility testing**: pip/pipx installation
- **Documentation testing**: README examples validation

### Test Fixtures
- **VallmCLI**: Helper for running CLI commands
- **temp_project**: Temporary project with multiple files
- **mock_llm**: Mock LLM provider for semantic tests

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **E2E Tests**: Full workflow testing
4. **Performance Tests**: Speed and resource usage
5. **Security Tests**: Vulnerability detection
6. **Compatibility Tests**: Cross-platform testing

### Workflow Triggers
- **Push**: main, develop branches
- **Pull Request**: main, develop branches  
- **Schedule**: Weekly (Sundays at 2 AM UTC)

### Test Jobs
1. **test-matrix**: Multi-OS, multi-Python version testing
2. **docker-tests**: Docker installation across systems
3. **integration-tests**: LLM integration testing
4. **performance-tests**: Large project validation
5. **security-tests**: Vulnerability scanning
6. **compatibility-tests**: pip/pipx installation
7. **documentation-tests**: README examples validation

### Coverage Reporting
- **Codecov**: Upload coverage reports
- **HTML reports**: Local coverage visualization
- **Threshold**: 85% coverage target

# Mock LLM responses for consistent testing
MOCK_LLM_RESPONSES = {
    "good_code": {"verdict": "pass", "score": 0.9},
    "bad_code": {"verdict": "review", "score": 0.3},
    "syntax_error": {"verdict": "fail", "score": 0.1}
}
```

# Temporary test projects
@pytest.fixture
def temp_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files...
        yield project_dir
```

### Test Metrics
- **Validation speed**: files/second
- **Memory usage**: peak memory consumption
- **Startup time**: CLI command initialization
- **LLM integration**: response time for semantic validation

# Large project validation
time vallm batch large_project --recursive

# Memory profiling
python -m memory_profiler vallm batch project --recursive
```

# Bandit security scan
bandit -r src/ -f json -o bandit-report.json

# Safety dependency check
safety check --json --output safety-report.json

# vallm security validation
vallm batch security_test --recursive --security
```

### Test Cases
- **Dangerous functions**: `os.system()`, `eval()`, `exec()`
- **Shell injection**: `subprocess` with shell=True
- **Hardcoded secrets**: passwords, API keys
- **SQL injection**: string concatenation in queries

### Common Issues
1. **LLM not available**: Use mock providers in tests
2. **Docker build failures**: Check base image availability
3. **Permission errors**: Use proper file permissions
4. **Network issues**: Mock external dependencies

# Run specific test
pytest tests/test_cli_e2e.py::TestCLICommands::test_help_command -v
```

### Adding New Tests
1. Create test file in `tests/` directory
2. Follow naming convention: `test_<module>.py`
3. Use pytest fixtures for setup/teardown
4. Add mock for external dependencies
5. Update CI/CD workflow if needed

### Test Requirements
- **Coverage**: New features must have test coverage
- **CI/CD**: All tests must pass in CI/CD
- **Documentation**: Update testing guide
- **Performance**: Add benchmarks for performance-critical code

### Planned Additions
- **Property-based testing**: Hypothesis integration
- **Contract testing**: API contract validation
- **Load testing**: High-volume validation testing
- **Chaos testing**: Fault injection testing
- **A/B testing**: Different algorithm comparisons

### Tool Integration
- **Selenium**: Web UI testing (if applicable)
- **Playwright**: End-to-end web testing
- **Locust**: Load testing framework
- **Chaos Monkey**: Fault injection testing
