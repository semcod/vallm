# Configuration and Customization Example

## Overview
This example demonstrates various configuration patterns for vallm.

## What it Tests
- **Configuration files**: JSON-based configuration
- **Environment variables**: Runtime configuration via env vars
- **Runtime configuration**: Programmatic settings changes
- **Profile switching**: Predefined configuration profiles
- **Threshold configuration**: Quality gate thresholds

## Demos Included

### 1. Configuration Files
```json
{
  "validators": {
    "syntax": {"enabled": true, "weight": 0.3},
    "security": {"enabled": true, "weight": 0.25}
  },
  "thresholds": {
    "pass": 0.8,
    "warning": 0.6
  }
}
```

### 2. Environment Variables
```bash
export VALLM_ENABLE_SYNTAX=true
export VALLM_ENABLE_SECURITY=true
export VALLM_OUTPUT_FORMAT=json
```

### 3. Runtime Configuration
```python
from vallm.config import VallmSettings

# Base settings
base = VallmSettings(enable_syntax=True, enable_imports=True)

# Create variant
security = VallmSettings(
    enable_syntax=base.enable_syntax,
    enable_security=True,
)
```

### 4. Configuration Profiles
Available profiles:
- `default`: Standard validation
- `security`: Security-focused
- `strict`: All validators enabled
- `minimal`: Fast syntax-only

### 5. Quality Thresholds
Configure pass/fail boundaries:
- Strict: 0.9
- Standard: 0.75
- Lenient: 0.6

## Running the Example
```bash
cd 16_configuration
python main.py
```

## Expected Output
- JSON configuration file creation/loading
- Environment variable parsing
- Profile switching demonstrations
- Threshold-based gate decisions

## Configuration Patterns

### Profile-Based Configuration
```python
profiles = {
    "security": {
        "syntax": True,
        "security": True,
        "complexity": False,
    },
    "strict": {
        "syntax": True,
        "security": True,
        "complexity": True,
    }
}

settings = VallmSettings(**profiles["security"])
```

### Environment-Based Configuration
```python
import os

settings = VallmSettings(
    enable_syntax=os.getenv("VALLM_SYNTAX", "true") == "true",
    enable_security=os.getenv("VALLM_SECURITY", "false") == "true",
)
```

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory.
