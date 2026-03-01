# Example 9: code2logic Integration

This example demonstrates integrating **vallm** with **code2logic** for logical code analysis and control flow visualization.

## Overview

- **code2logic**: Extracts logical structures, control flow, functions
- **vallm**: Validates code quality and complexity
- **Combined**: Deep logical analysis with quality validation

## Prerequisites

```bash
pip install code2logic vallm
```

## What It Demonstrates

1. **Function Extraction** — code2logic extracts all functions and their signatures
2. **Control Flow Analysis** — branches, loops, conditions analysis
3. **Quality Validation** — vallm checks syntax, complexity, imports
4. **Call Graph Building** — vallm's graph builder shows dependencies
5. **Visualization** — Generate DOT graphs for control flow

## Running the Example

```bash
cd examples/09_code2logic_integration
python main.py
```

## Expected Output

```
🚀 code2logic + vallm Integration Example
============================================================

============================================================
Analyzing with code2logic...
============================================================
Found 2 functions:
  - process_order (8 branches)
  - calculate_discount (6 branches)

============================================================
Validating with vallm...
============================================================

Verdict: pass
Score: 0.95

Validator results:
  ✓ syntax: 1.00
  ✓ imports: 1.00
  ⚠ complexity: 0.85
      - process_order has high cyclomatic complexity

============================================================
Building call graph...
============================================================
Functions: ['process_order', 'calculate_discount']
Classes: ['OrderStatus']
Imports: 3
Calls: 2

📊 Report saved to .vallm/code2logic_integration_report.json

💡 Recommendations:
   - Simplify 1 high-complexity function

============================================================
FINAL SUMMARY
============================================================
Quality Score: 0.95/1.0
Verdict: PASS
```

## How It Works

### 1. Extract Functions

```python
from code2logic import extract_functions

functions = extract_functions(code)
for func in functions:
    print(f"{func['name']} ({func['complexity']} branches)")
```

### 2. Analyze Control Flow

```python
from code2logic import analyze_control_flow

flow = analyze_control_flow(code, "process_order")
print(f"Branches: {len(flow['branches'])}")
print(f"Loops: {len(flow['loops'])}")
print(f"Conditions: {len(flow['conditions'])}")
```

### 3. Validate with vallm

```python
from vallm import Proposal, validate

proposal = Proposal(code=code, language="python")
result = validate(proposal)
```

### 4. Build Call Graph

```python
from vallm.core.graph_builder import build_python_graph

graph = build_python_graph(code, "module_name")
print(f"Functions: {graph.functions}")
print(f"Calls: {len(graph.calls)}")
```

### 5. Visualize

```python
from code2logic.visualize import generate_dot

dot = generate_dot(code)
# Render with Graphviz
# dot -Tpng control_flow.dot -o flow.png
```

## Report Format

```json
{
  "tools": {
    "code2logic": true,
    "vallm": true
  },
  "analysis": {
    "logical_structure": {
      "functions": 2,
      "control_flow": {
        "branches": 8,
        "loops": 1,
        "conditions": 6
      }
    },
    "quality_validation": {
      "verdict": "pass",
      "score": 0.95
    },
    "call_graph": {
      "functions": 2,
      "calls": 2
    }
  },
  "recommendations": [
    "Simplify 1 high-complexity function"
  ]
}
```

## Use Cases

### Refactoring Assistant

```python
# Find complex functions that need refactoring
def find_refactoring_candidates(codebase):
    candidates = []
    
    for file in codebase:
        # Logical analysis
        functions = extract_functions(file)
        
        for func in functions:
            flow = analyze_control_flow(file, func['name'])
            
            # Quality check
            proposal = Proposal(code=file, language="python")
            result = validate(proposal)
            
            if flow['branches'] > 10 or result.score < 0.7:
                candidates.append({
                    'function': func['name'],
                    'branches': flow['branches'],
                    'score': result.score
                })
    
    return candidates
```

### Complexity Dashboard

```python
# Generate complexity metrics dashboard
metrics = {
    'total_functions': len(functions),
    'avg_complexity': sum(f['complexity'] for f in functions) / len(functions),
    'high_complexity': sum(1 for f in functions if f['complexity'] > 10),
    'quality_score': vallm_result['score']
}
```

### Documentation Generation

```python
# Auto-generate documentation from analysis
for func in functions:
    flow = analyze_control_flow(code, func['name'])
    
    doc = f"""
## {func['name']}

**Complexity**: {func['complexity']} branches
**Quality Score**: {validate(Proposal(code=func['code'], language='python')).score:.2f}

### Control Flow
- Branches: {len(flow['branches'])}
- Loops: {len(flow['loops'])}
- Conditions: {len(flow['conditions'])}
"""
    print(doc)
```

## Troubleshooting

### code2logic not found

```bash
pip install code2logic
```

### Graphviz not installed

```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Windows
choco install graphviz
```

## Further Reading

- [code2logic documentation](https://github.com/tom-sapletta/code2logic)
- [vallm graph analysis](../04_graph_analysis/README.md)
- [vallm complexity validation](../01_basic_validation/README.md)
