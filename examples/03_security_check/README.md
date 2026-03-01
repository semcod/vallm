# Security Check Example

## Overview
This example demonstrates vallm's security validation capabilities, focusing on detecting common security vulnerabilities in Python code.

## What it Tests
- **Pattern-based security checks**: Identifies dangerous function calls
- **AST-based detection**: Analyzes code structure for security issues
- **Common vulnerability patterns**: eval(), exec(), os.system, pickle.loads, etc.

## Code Samples
The example compares two code implementations:
1. **Insecure code** - Contains multiple security vulnerabilities:
   - `eval()` on user input
   - `exec()` with dynamic strings
   - `os.system()` with user data
   - `pickle.loads()` unsafe deserialization
   - `yaml.load()` without safe loader
   - Hardcoded API keys

2. **Secure code** - Safe alternatives:
   - `json.loads()` for structured data
   - `subprocess.run()` with proper argument handling
   - `yaml.safe_load()` for YAML parsing

## Running the Example
```bash
cd 03_security_check
python main.py
```

## Expected Output
- Security scores (0.0-1.0) for each code sample
- Detailed list of security issues found
- Comparison between insecure and secure implementations

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory, including:
- Security vulnerability reports
- Risk assessments
- Recommendations for fixes
