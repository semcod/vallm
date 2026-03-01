# Multi-language Validation Example

## Overview
This example demonstrates vallm's multi-language code validation capabilities using tree-sitter parsers for cross-language analysis.

## What it Tests
- **Multi-language syntax validation**: JavaScript, TypeScript, C, Go, Rust, and Java support
- **Tree-sitter parsing**: Universal parsing for different programming languages
- **Cross-language complexity analysis**: Language-agnostic complexity metrics via lizard
- **Language-specific import validation**: Import/include checks for each language
- **Security pattern detection**: Language-specific security patterns
- **Consistent validation interface**: Same API for all supported languages

## Code Samples
The example validates code in multiple languages:
1. **JavaScript (good/bad)** - Quicksort implementation with/without syntax errors
2. **TypeScript (good/bad)** - Interface and function with/without syntax errors
3. **C (good/bad)** - GCD algorithm with/without syntax errors
4. **Go (good/bad)** - Fibonacci function with/without syntax errors
5. **Rust (good/bad)** - Factorial function with/without syntax errors
6. **Java (good/bad)** - Calculator class with/without syntax errors

## Supported Languages

### Full Support (Syntax + Complexity + Imports + Security)
- **Python** - Full AST analysis, radon complexity, import resolution, bandit integration

### Tree-sitter Support (Syntax + Complexity + Imports + Security)
- **JavaScript** - ES6+ syntax validation, Node.js built-in checks
- **TypeScript** - Type checking and syntax validation
- **C** - C99/C11 standard compliance
- **C++** - Modern C++ syntax validation
- **Go** - Go modules and standard library checks
- **Rust** - Unsafe block detection, crate validation
- **Java** - Package validation, runtime exec checks

### Partial Support (Syntax + Complexity)
- **Ruby** - Syntax validation and complexity
- **PHP** - Syntax validation and complexity
- **Swift** - Syntax validation and complexity
- **Kotlin** - Syntax validation and complexity
- **Scala** - Syntax validation and complexity

## Running the Example
```bash
cd 06_multilang_validation
python main.py
```

## Expected Output
- Syntax validation results for each language
- Complexity analysis across different languages
- Import validation for supported languages
- Security pattern detection
- Consistent scoring and verdict system
- Language-specific error messages and issues

## Configuration Notes
- Import validation is enabled for all supported languages
- Security checks are language-specific
- Complexity analysis uses lizard for multi-language support
- Semantic analysis requires LLM configuration

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory, including:
- Multi-language validation reports
- Cross-language complexity metrics
- Syntax error details for each language
- Comparative analysis results
