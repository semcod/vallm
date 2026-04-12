# CLI Usage Example

## Overview
This example demonstrates using the vallm command-line interface programmatically.

## What it Tests
- **Single file validation**: CLI validation of individual files
- **Batch validation**: CLI batch processing
- **Output formats**: Text and JSON output handling
- **Programmatic invocation**: Using CLI via subprocess
- **CI/CD integration**: Check command for automation

## Prerequisites
Ensure vallm CLI is available:
```bash
pip install -e /path/to/vallm
# or
python -m pip install vallm
```

## Demos Included

### 1. Single File Validation
```bash
python -m vallm validate file.py --format json
```

### 2. Batch Validation
```bash
python -m vallm batch ./directory/
```

### 3. Output Formats
- Text format (human-readable)
- JSON format (machine-parseable)

### 4. Programmatic CLI Usage
Using Python's `subprocess` module to invoke CLI commands and parse results.

### 5. Check Command (CI/CD)
Exit codes for automation:
- `0` = pass
- Non-zero = fail

## Running the Example
```bash
cd 15_cli_usage
python main.py
```

## Expected Output
- CLI command demonstrations
- Parsed validation results
- Exit code handling
- Error output processing

## CLI Commands Reference

### Validate Single File
```bash
vallm validate <file> [--format {text,json}]
```

### Batch Validate
```bash
vallm batch <directory> [--format {text,json,toon}]
```

### CI Check (Exit Codes)
```bash
vallm check <file>
# Exit 0 = pass, non-zero = fail
```

## Programmatic Usage Pattern
```python
import subprocess

result = subprocess.run(
    ["python", "-m", "vallm", "validate", "file.py", "--format", "json"],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
if data["verdict"] == "PASS":
    print("Code is valid!")
```

## CI/CD Integration
```yaml
# .github/workflows/validate.yml
- name: Validate Code
  run: |
    python -m vallm check src/
    if [ $? -ne 0 ]; then
      echo "Validation failed"
      exit 1
    fi
```

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory.
