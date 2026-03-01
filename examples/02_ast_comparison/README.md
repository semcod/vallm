# AST Comparison Example

## Overview
This example demonstrates vallm's Abstract Syntax Tree (AST) comparison and structural analysis capabilities.

## What it Tests
- **Tree-sitter parsing**: Multi-language code parsing and analysis
- **Python AST normalization**: Standardizing Python AST structures for comparison
- **Similarity scoring**: Computing structural similarity between code snippets
- **Structural diff analysis**: Identifying differences between code versions

## Code Samples
The example analyzes several code implementations:
1. **Python functions** - `add()` vs `sum_values()` (semantically similar)
2. **Different implementations** - `add()` vs `multiply()` (semantically different)
3. **Multi-language examples** - JavaScript and C code for comparison

## Running the Example
```bash
cd 02_ast_comparison
python main.py
```

## Expected Output
- AST similarity scores between code pairs
- Tree-sitter node counts and error counts
- Structural diff summaries showing added/removed node types

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory, including:
- AST comparison reports
- Similarity matrices
- Structural diff details
- Multi-language parsing results
