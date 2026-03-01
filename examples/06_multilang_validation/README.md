# Multi-language Validation Example

## Overview
This example demonstrates vallm's multi-language code validation capabilities using tree-sitter parsers for cross-language analysis.

## What it Tests
- **Multi-language syntax validation**: JavaScript, C, and TypeScript support
- **Tree-sitter parsing**: Universal parsing for different programming languages
- **Cross-language complexity analysis**: Language-agnostic complexity metrics
- **Consistent validation interface**: Same API for all supported languages

## Code Samples
The example validates code in multiple languages:
1. **JavaScript (good)** - Proper quicksort implementation
2. **JavaScript (bad)** - Missing semicolons and brackets
3. **C (good)** - Correct GCD algorithm implementation
4. **C (bad)** - Missing semicolon causing syntax error

## Supported Languages
- **JavaScript** - ES6+ syntax validation
- **C** - C99/C11 standard compliance
- **TypeScript** - Type checking and syntax validation
- **Python** - Full Python 3.x support (shown in other examples)

## Running the Example
```bash
cd 06_multilang_validation
python main.py
```

## Expected Output
- Syntax validation results for each language
- Complexity analysis across different languages
- Consistent scoring and verdict system
- Language-specific error messages and issues

## Configuration Notes
- Import validation is disabled for non-Python languages
- Security checks are language-dependent
- Semantic analysis requires LLM configuration

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory, including:
- Multi-language validation reports
- Cross-language complexity metrics
- Syntax error details for each language
- Comparative analysis results
