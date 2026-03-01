# Example 10: MCP Demo - code2llm + Ollama + vallm

This example demonstrates a complete **MCP (Model Context Protocol)** workflow:

1. **code2llm** analyzes existing legacy code structure
2. **Ollama** (Qwen 2.5 Coder 7B) generates refactored code
3. **vallm** validates the LLM response for correctness
4. If validation fails, feedback is sent back to Ollama for corrections
5. Process repeats until code passes all validations

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  code2llm   │────▶│   Ollama    │────▶│    vallm    │
│  (analyze)  │     │  (generate) │     │ (validate)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
       ▲                                       │
       └───────────────────────────────────────┘
          (feedback loop if validation fails)
```

## Prerequisites

- Docker
- 8GB+ RAM (for running Qwen 2.5 Coder 7B)
- ~10GB free disk space (for Ollama model)

## Quick Start

```bash
cd examples/10_mcp_ollama_demo
./run.sh
```

This will:
1. Build Docker image with Ollama
2. Pull Qwen 2.5 Coder 7B model (first time only)
3. Analyze legacy code with code2llm
4. Run the MCP workflow
5. Show logs and results

## What This Demonstrates

### Legacy Code Issues

The example includes `legacy_code/order_processor.py` with intentional issues:

- **Security vulnerabilities**: `eval()`, `pickle`, SQL injection, command injection
- **High complexity**: Deeply nested conditionals (cyclomatic complexity > 15)
- **Duplicate code**: Two identical email validation functions
- **Magic numbers**: Hardcoded shipping costs
- **Dead code**: Unused variables and functions
- **Hardcoded credentials**: API keys in source code
- **SOLID violations**: OrderManager class has too many responsibilities

### The Workflow

```
Step 1: Analyze
  code2llm → Extracts functions, classes, complexity metrics

Step 2: Validate Legacy
  vallm → Identifies security issues and complexity problems

Step 3: Generate Refactoring
  Ollama → Receives prompt with legacy code and issues
         → Generates refactored Python code

Step 4: Validate Refactored
  vallm → Checks syntax, imports, complexity, security
        → If issues found → Send feedback to Ollama
        → If passed → Save final code

Step 5: Iterate (if needed)
  Repeat steps 3-4 up to 3 times until code passes
```

## Running Manually

### Start Docker Container

```bash
# Build and start
docker build -t vallm-mcp-demo .
docker run -d --name vallm-mcp-demo -p 11434:11434 vallm-mcp-demo

# Wait for model download
docker logs -f vallm-mcp-demo
```

### Run MCP Demo

```bash
# Inside container
docker exec -it vallm-mcp-demo bash
python mcp_demo.py

# Or from host with Ollama running locally
python mcp_demo.py --file legacy_code/order_processor.py
```

### View Logs

```bash
# Real-time logs
tail -f mcp_demo.log

# Full output
cat mcp-demo-output.log
```

## Expected Output

### Successful Run

```
======================================================================
Step 1: Analyzing code structure with code2llm
======================================================================
✓ Analysis complete
  Functions found: 12
  Classes found: 1
  Complexity: high

======================================================================
Step 2: Validating legacy code with vallm
======================================================================

Validation Result: FAIL (score: 0.45)
  ✗ syntax: 1.00
  ✓ imports: 0.95
  ⚠ complexity: 0.35
  ✗ security: 0.00
    [error] security: eval() usage detected
    [error] security: pickle usage detected
    [error] security: SQL injection vulnerability
    [warning] security: hardcoded credentials

======================================================================
Step 3: Sending to Ollama (Qwen 2.5 Coder 7B) for refactoring
======================================================================
Prompt sent to LLM (truncated):
You are an expert Python code reviewer...

======================================================================
Step 4: Received LLM response
======================================================================
REFACTORED CODE:
```python
class OrderProcessor:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def process_order(self, order_data: dict) -> float:
        \"\"\"Process order with validation.\"\"\"
        if not self._validate_order(order_data):
            return 0.0
        
        items = order_data.get('items', [])
        total = self._calculate_total(items)
        
        if total > 100:
            total *= 0.9  # 10% discount
        
        return total
    
    def _validate_order(self, data: dict) -> bool:
        # ...
```

======================================================================
Step 5: Validating refactored code (iteration 1)
======================================================================

Validation Result: PASS (score: 0.95)
  ✓ syntax: 1.00
  ✓ imports: 1.00
  ✓ complexity: 0.90
  ✓ security: 1.00

======================================================================
✓ SUCCESS: Code passed all validations!
======================================================================
Refactoring successful after 1 iteration(s)

✓ Final code saved to: /app/refactored_output.py
```

### Failed Validation with Retry

If the LLM generates code that doesn't pass validation:

```
======================================================================
Step 5: Validating refactored code (iteration 1)
======================================================================

Validation Result: REVIEW (score: 0.75)
  ✓ syntax: 1.00
  ✓ imports: 1.00
  ⚠ complexity: 0.65
  ✓ security: 1.00
      - complexity: process_order has cyclomatic complexity 12 (max: 10)

⚠ Validation failed, requesting corrections from LLM...

LLM CORRECTION (iteration 2):
```python
# ... improved code with reduced complexity
```
```

## Files

| File | Description |
|------|-------------|
| `Dockerfile` | Docker image with Ollama and dependencies |
| `docker-entrypoint.sh` | Container startup script |
| `mcp_demo.py` | Main MCP workflow script |
| `run.sh` | Automated demo runner with logging |
| `legacy_code/order_processor.py` | Example code with issues |
| `mcp_demo.log` | Detailed debug logs (generated) |
| `mcp-demo-output.log` | Full demo output (generated) |
| `refactored_output.py` | Final refactored code (generated) |

## Configuration

### Environment Variables

```bash
# Ollama configuration
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=qwen2.5-coder:7b

# Demo configuration
export MAX_ITERATIONS=3
export TEMPERATURE=0.2
```

### Command Line Options

```bash
python mcp_demo.py \
    --file legacy_code/order_processor.py \
    --max-iterations 5
```

## How It Works

### 1. code2llm Analysis

```python
from code2llm import analyze_file

result = analyze_file("order_processor.py")
print(f"Functions: {len(result['functions'])}")
print(f"Complexity: {result['complexity']}")
```

### 2. vallm Validation

```python
from vallm import Proposal, validate, VallmSettings

settings = VallmSettings(
    enable_syntax=True,
    enable_security=True,
    enable_complexity=True
)

proposal = Proposal(code=code, language="python")
result = validate(proposal, settings)

if result.verdict.value == "pass":
    print("✓ Code is valid")
else:
    for issue in result.all_issues:
        print(f"✗ {issue.validator}: {issue.message}")
```

### 3. Ollama Integration

```python
import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "qwen2.5-coder:7b",
    "prompt": prompt,
    "stream": False
})

refactored_code = response.json()['response']
```

### 4. Feedback Loop

```python
# If validation fails, send feedback to LLM
if validation['verdict'] != 'pass':
    correction_prompt = f"""
Previous code has issues:
{chr(10).join(f"- [{i['severity']}] {i['message']}" for i in validation['issues'])}

Fix all issues and return corrected Python code.
"""
    
    new_code = call_ollama(correction_prompt)
```

## Troubleshooting

### Ollama Connection Error

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check container logs
docker logs vallm-mcp-demo

# Restart container
docker restart vallm-mcp-demo
```

### Model Download Issues

```bash
# Manually pull model
docker exec vallm-mcp-demo ollama pull qwen2.5-coder:7b

# Check available models
docker exec vallm-mcp-demo ollama list
```

### Validation Always Fails

If LLM consistently produces invalid code:

1. Check `mcp_demo.log` for detailed error messages
2. Increase `MAX_ITERATIONS` in run.sh
3. Lower `TEMPERATURE` for more deterministic output
4. Review the prompt in `mcp_demo.py` and adjust

## Advanced Usage

### Custom Legacy Code

```bash
# Analyze your own code
python mcp_demo.py --file /path/to/your/legacy_code.py --max-iterations 5
```

### Integration with CI

```yaml
# .github/workflows/refactor.yml
- name: Refactor with MCP
  run: |
    docker run -v $(pwd):/app vallm-mcp-demo \
      python /app/mcp_demo.py --file /app/src/legacy.py
    
    if [ -f refactored_output.py ]; then
      cp refactored_output.py src/legacy_refactored.py
    fi
```

## Architecture Benefits

1. **Automated Code Review**: No manual intervention needed
2. **Security-First**: vallm blocks security vulnerabilities
3. **Self-Correcting**: LLM learns from validation feedback
4. **Observable**: Complete logs of all decisions
5. **Reproducible**: Same input → same validation process

## References

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Qwen 2.5 Coder](https://huggingface.co/Qwen)
- [vallm Security Validation](../../src/vallm/validators/security.py)
- [code2llm Analysis](https://github.com/tom-sapletta/code2llm)
