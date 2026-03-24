# MCP Vallm Integration

This directory contains the MCP (Model Context Protocol) integration for vallm, exposing vallm validators as MCP tools for LLM tool calling.

## Quick Start

```bash
# Start the MCP server from project root
python3 mcp_server.py

# Or start the packaged server directly
python3 -m mcp.server.self_server

# Test the integration
python3 test_mcp.py

# Run the Docker e2e workflow
bash mcp/tests/run_e2e.sh
```

## Files

- `mcp/server/_tools_vallm.py` - Core MCP tools implementation
- `mcp/server/self_server.py` - MCP server for vallm integration
- `mcp_server.py` - Startup script (project root)
- `test_mcp.py` - Comprehensive manual test suite
- `mcp/tests/container_e2e.py` - Container-side end-to-end runner
- `mcp/tests/test_e2e.py` - Host-side build/run and integration checks

## Available Tools

### validate_syntax
Multi-language syntax checking using vallm SyntaxValidator
- **Endpoint**: `POST /mcp/self/tools/validate_syntax`
- **Parameters**: 
  - `code` (required): Source code to validate
  - `language` (optional): Programming language (default: "python")
  - `filename` (optional): Filename for context

### validate_imports
Import resolution validation using vallm ImportValidator
- **Endpoint**: `POST /mcp/self/tools/validate_imports`
- **Parameters**:
  - `code` (required): Source code to validate
  - `language` (optional): Programming language (default: "python") 
  - `filename` (optional): Filename for context

### validate_security
Security issue detection using vallm SecurityValidator
- **Endpoint**: `POST /mcp/self/tools/validate_security`
- **Parameters**:
  - `code` (required): Source code to validate
  - `language` (optional): Programming language (default: "python")
  - `filename` (optional): Filename for context
- **Detects**: eval, exec, secrets, SQL injection, command injection, etc.

### validate_code
Full pipeline validation combining multiple validators
- **Endpoint**: `POST /mcp/self/tools/validate_code`
- **Parameters**:
  - `code` (required): Source code to validate
  - `language` (optional): Programming language (default: "python")
  - `filename` (optional): Filename for context
  - `reference_code` (optional): Reference code for regression testing
  - `enable_syntax` (optional): Enable syntax validation (default: true)
  - `enable_imports` (optional): Enable import validation (default: true)
  - `enable_security` (optional): Enable security validation (default: true)
  - `enable_complexity` (optional): Enable complexity validation (default: true)
  - `enable_regression` (optional): Enable regression validation (default: false)

## Usage

### Starting the MCP Server

```bash
PYTHONPATH=/path/to/vallm/src python3 -m mcp.server.self_server
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vallm": {
      "command": "python3",
      "args": ["/path/to/vallm/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/vallm/src"
      }
    }
  }
}
```

### Example Tool Call

```json
{
  "method": "tools/call",
  "params": {
    "name": "validate_security",
    "arguments": {
      "code": "import os; os.system('rm -rf /')",
      "language": "python"
    }
  }
}
```

## Response Format

All tools return a consistent response format:

```json
{
  "success": true,
  "validator": "security",
  "score": 0.3,
  "weight": 1.5,
  "confidence": 0.9,
  "verdict": "fail",
  "issues": [
    {
      "message": "Use of os.system() — prefer subprocess",
      "severity": "warning",
      "line": 2,
      "column": null,
      "rule": "security.os_system"
    }
  ],
  "details": {}
}
```

### Verdict Values

- `pass`: Score >= 0.8 and no errors
- `review`: Score >= 0.5 and no errors  
- `fail`: Score < 0.5 or has errors
- `error`: Exception occurred during validation

## Testing

```bash
# Test syntax validation
PYTHONPATH=src python3 -c "from mcp.server._tools_vallm import validate_syntax; print(validate_syntax('print(\"hello\")', 'python')['verdict'])"

# Test security validation
PYTHONPATH=src python3 -c "from mcp.server._tools_vallm import validate_security; result = validate_security('eval(\"1+1\")', 'python'); print(result['verdict'], len(result['issues']))"

# Test full pipeline
PYTHONPATH=src python3 -c "from mcp.server._tools_vallm import validate_code; code = 'def test(): eval(\"1+1\")'; result = validate_code(code, 'python'); print(result['verdict'], result['score'])"

# Run the Docker container-side E2E runner locally
python3 mcp/tests/container_e2e.py
```
