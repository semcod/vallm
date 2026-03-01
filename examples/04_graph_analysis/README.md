# Graph Analysis Example

## Overview
This example demonstrates vallm's code graph analysis capabilities, including import/call graph building and structural regression detection.

## What it Tests
- **Import graph analysis**: Tracks module dependencies
- **Call graph building**: Maps function call relationships
- **Structural diffing**: Compares code versions for changes
- **Breaking change detection**: Identifies potentially breaking modifications

## Code Samples
The example analyzes two versions of the same codebase:
1. **Before code** - Simple implementation with:
   - Basic imports (os, json, pathlib)
   - Simple functions for config reading and data processing
   - Direct function calls

2. **After code** - Enhanced version with:
   - Updated imports (json, yaml, dataclasses)
   - Dataclass for structured config
   - Additional validation function
   - Modified function signatures

## Running the Example
```bash
cd 04_graph_analysis
python main.py
```

## Expected Output
- Import graphs showing module dependencies
- Function and class inventories
- Call relationship mappings
- Structural diff highlighting:
  - Added/removed imports and functions
  - Breaking change warnings
  - Change impact analysis

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory, including:
- Graph representations (imports, calls, functions)
- Diff reports and change summaries
- Breaking change assessments
- Structural impact analysis
