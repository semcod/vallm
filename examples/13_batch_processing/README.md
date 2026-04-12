# Batch Processing Example

## Overview
This example demonstrates vallm's batch validation capabilities for processing multiple files efficiently.

## What it Tests
- **Directory scanning**: Automatically find files to validate
- **Batch validation**: Process multiple files in one operation
- **TOON reports**: Generate formatted batch reports
- **Result aggregation**: Summarize validation across files

## Code Samples
The example creates and validates three test files:
1. **good_file.py** - Clean code (should PASS)
2. **bad_file.py** - Syntax errors and security issues (should FAIL)
3. **complex_file.py** - High complexity code (should get warnings)

## Running the Example
```bash
cd 13_batch_processing
python main.py
```

## Expected Output
- File discovery and listing
- Individual validation results per file
- TOON-formatted batch report
- Summary statistics (passed/failed/warning counts)

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory.

## API Usage
```python
from vallm import batch_validate, VallmSettings

settings = VallmSettings(
    enable_syntax=True,
    enable_imports=True,
    enable_complexity=True,
    enable_security=True,
)

results = batch_validate(
    paths=["file1.py", "file2.py"],
    settings=settings,
)
```
