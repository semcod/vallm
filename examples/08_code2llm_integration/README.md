# Example 8: code2llm Integration

This example demonstrates integrating **vallm** with **code2llm** for comprehensive code analysis and validation.

## Overview

- **code2llm**: Analyzes code structure, extracts insights, generates TOON format reports
- **vallm**: Validates code quality through the 4-tier pipeline
- **Combined**: Full project analysis with quality gates

## Prerequisites

```bash
pip install code2llm vallm
```

## What It Demonstrates

1. **Project Structure Analysis** — code2llm analyzes file structure and language distribution
2. **Quality Validation** — vallm validates each file through syntax, imports, complexity checks
3. **Combined Reporting** — unified report with both structural and quality metrics
4. **Batch Processing** — process entire project directories

## Running the Example

```bash
cd examples/08_code2llm_integration
python main.py
```

## Expected Output

```
🚀 code2llm + vallm Integration Example
============================================================

📁 Creating sample project...
   Created at: sample_project

============================================================
Analyzing with code2llm...
============================================================
Analyzing project structure...
Found 3 Python files

============================================================
Validating with vallm...
============================================================
✓ math_utils.py: pass (score: 1.00)
✓ string_utils.py: pass (score: 1.00)
✓ main.py: pass (score: 1.00)

📊 Report saved to .vallm/code2llm_integration_report.json

============================================================
INTEGRATION SUMMARY
============================================================
Total files analyzed: 3
Passed: 3
Failed: 0

🎉 All files passed quality checks!
```

## How It Works

### 1. Create Sample Project

```python
SAMPLE_PROJECT = {
    "math_utils.py": '''...''',
    "string_utils.py": '''...''',
    "main.py": '''...''',
}
```

### 2. Analyze Structure

```python
from code2llm import analyze_directory

# Get project structure
result = analyze_directory(project_path)
print(f"Found {len(result['files'])} files")
```

### 3. Validate Quality

```python
from vallm import Proposal, validate

# Validate each file
for file_path in project_path.rglob("*.py"):
    code = file_path.read_text()
    proposal = Proposal(code=code, language="python")
    result = validate(proposal)
    print(f"{file_path}: {result.verdict.value}")
```

### 4. Generate Report

```json
{
  "analysis_tools": {
    "code2llm": true,
    "vallm": true
  },
  "project_structure": {
    "files": 3,
    "languages": {"Python": 3}
  },
  "quality_validation": {
    "files": [
      {"file": "math_utils.py", "verdict": "pass", "score": 1.0}
    ]
  },
  "summary": {
    "total_files": 3,
    "passed": 3,
    "failed": 0
  }
}
```

## Use Cases

### CI/CD Pipeline

```bash
# Analyze and validate entire codebase
python -m vallm batch src/ --recursive --format json > validation.json
code2llm analyze ./ --format toon > analysis.toon

# Combine reports
python combine_reports.py
```

### Pre-commit Hook

```python
#!/usr/bin/env python
"""Pre-commit hook using code2llm + vallm."""

import subprocess
import sys

# Analyze staged files
result = subprocess.run(
    ["code2llm", "analyze", "--staged"],
    capture_output=True
)

# Validate staged files
result = subprocess.run(
    ["vallm", "batch", "--staged", "--fail-fast"],
    capture_output=True
)

if result.returncode != 0:
    print("❌ Validation failed")
    sys.exit(1)
```

### IDE Integration

```python
# VS Code extension using both tools
from code2llm import get_file_info
from vallm import validate_file

def on_file_save(file_path):
    # Get structural info
    info = get_file_info(file_path)
    
    # Validate quality
    result = validate_file(file_path)
    
    # Show inline diagnostics
    show_diagnostics(file_path, result.issues)
```

## API Reference

### code2llm Functions

- `analyze_directory(path)` — Analyze entire directory
- `analyze_file(path)` — Analyze single file
- `TOONFormat.parse(path)` — Parse TOON format output

### vallm Integration

```python
from vallm import Proposal, validate, VallmSettings
from vallm.core.languages import detect_language

# Auto-detect language
lang = detect_language(file_path)

# Create proposal with detected language
proposal = Proposal(
    code=code,
    language=lang.tree_sitter_id if lang else "python"
)

# Validate
result = validate(proposal)
```

## Troubleshooting

### code2llm not found

```bash
pip install code2llm
```

### Import errors

```bash
# Ensure both packages are in same environment
pip install code2llm vallm
```

## Further Reading

- [code2llm documentation](https://github.com/tom-sapletta/code2llm)
- [vallm documentation](../../README.md)
- [Batch validation](../07_multi_language/README.md)
