# Basic Validation Example

## Overview
This example demonstrates vallm's basic Python code validation capabilities using the default pipeline (Tier 1 & 2 validators).

## What it Tests
- **Syntax validation**: Checks for Python syntax errors
- **Import validation**: Validates import statements and dependencies  
- **Complexity validation**: Analyzes code complexity and identifies overly complex structures

## Code Samples
The example validates three different code samples:
1. **Good code** - Clean Fibonacci implementation (should PASS)
2. **Bad code** - Contains syntax error (should FAIL)
3. **Complex code** - Deeply nested conditional structure (should get warnings)

## Running the Example
```bash
cd 01_basic_validation
python main.py
```

## Expected Output
- Validation verdict (PASS/FAIL/WARNING)
- Weighted score (0.0-1.0)
- Individual validator scores
- Detailed issues found (if any)

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory, including:
- Validation reports
- Score breakdowns
- Issue details
