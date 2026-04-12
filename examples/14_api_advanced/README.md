# Advanced API Usage Example

## Overview
This example demonstrates advanced patterns for using the vallm API programmatically.

## What it Tests
- **Proposal creation**: Different methods for creating validation proposals
- **Settings customization**: Configuring validators for specific use cases
- **Result interpretation**: Programmatically analyzing validation results
- **Workflow integration**: Using vallm in CI/CD pipelines

## Demos Included

### 1. Proposal Creation Methods
- From code strings
- From file paths (commented)
- With custom metadata

### 2. Settings Customization
- Default settings
- Security-focused configuration
- Performance-focused configuration
- Full validation mode

### 3. Result Interpretation
- Overall verdict analysis
- Per-validator score breakdown
- Issue categorization
- Decision recommendations

### 4. CI/CD Workflow Integration
- Quality gate thresholds
- Pass/fail decisions
- JSON report generation
- Deployment gate logic

## Running the Example
```bash
cd 14_api_advanced
python main.py
```

## Expected Output
- Multiple demo sections with detailed explanations
- Validation results with interpretation
- Quality gate decision logic
- JSON-formatted reports

## Use Cases
- **CI/CD Integration**: Automate code quality gates
- **Custom Tools**: Build validation into your workflows
- **Reporting**: Generate structured validation reports
- **Decision Automation**: Programmatic pass/fail decisions

## Code Patterns

### Quality Gate Pattern
```python
from vallm import Proposal, validate, VallmSettings

settings = VallmSettings(enable_syntax=True, enable_security=True)
proposal = Proposal(code=code, language="python")
result = validate(proposal, settings)

if result.weighted_score >= 0.8:
    print("PASS - Proceed with deployment")
else:
    print("FAIL - Fix issues first")
```

### Custom Settings Pattern
```python
from vallm.config import VallmSettings

# Security audit
security_settings = VallmSettings(
    enable_syntax=True,
    enable_security=True,
    enable_complexity=False,
    enable_semantic=False,
)
```

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory.
