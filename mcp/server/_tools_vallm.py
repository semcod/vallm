#!/usr/bin/env python3
"""
MCP Vallm Integration - vallm validators exposed as MCP tools

Provides MCP endpoints for code validation:
- POST /mcp/self/tools/validate_syntax — Multi-language syntax checking
- POST /mcp/self/tools/validate_imports — Import resolution validation  
- POST /mcp/self/tools/validate_security — Security issue detection
- POST /mcp/self/tools/validate_code — Full pipeline validation

Registered in self_server.py with TOOL_SCHEMA_VALLM for LLM tool calling.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from vallm.core.proposal import Proposal
from vallm.validators.syntax import SyntaxValidator
from vallm.validators.imports.wrapper import ImportValidator
from vallm.validators.security import SecurityValidator
from vallm.validators.complexity import ComplexityValidator
from vallm.validators.regression import RegressionValidator
from vallm.scoring import ValidationResult


def _format_issue(issue) -> Dict[str, Any]:
    """Serialize a single Issue to a plain dict."""
    return {
        "message": issue.message,
        "severity": issue.severity.value,
        "line": issue.line,
        "column": issue.column,
        "rule": issue.rule,
    }


def _compute_verdict(overall_score: float, error_count: int) -> str:
    """Derive pass/review/fail verdict from score and error count."""
    if overall_score >= 0.8 and error_count == 0:
        return "pass"
    if overall_score >= 0.5 and error_count == 0:
        return "review"
    return "fail"


def _run_validators(
    proposal: Proposal,
    enable_syntax: bool,
    enable_imports: bool,
    enable_security: bool,
    enable_complexity: bool,
    enable_regression: bool,
    reference_code: Optional[str],
):
    """Run enabled validators and return (results, total_score, total_weight, all_issues)."""
    validators_to_run = []
    if enable_syntax:
        validators_to_run.append(SyntaxValidator())
    if enable_imports:
        validators_to_run.append(ImportValidator())
    if enable_security:
        validators_to_run.append(SecurityValidator())
    if enable_complexity:
        validators_to_run.append(ComplexityValidator())
    if enable_regression and reference_code:
        validators_to_run.append(RegressionValidator())

    results = []
    total_score = 0.0
    total_weight = 0.0
    all_issues = []
    for v in validators_to_run:
        r = v.validate(proposal, {})
        results.append(r)
        total_score += r.score * r.weight
        total_weight += r.weight
        all_issues.extend(r.issues)
    return results, total_score, total_weight, all_issues


def _build_pipeline_response(
    results,
    total_weight: float,
    verdict: str,
    all_issues: List,
) -> Dict[str, Any]:
    """Build the full-pipeline success response dict."""
    error_count = sum(1 for i in all_issues if i.severity.value == "error")
    warning_count = sum(1 for i in all_issues if i.severity.value == "warning")
    overall_score = sum(r.score * r.weight for r in results) / total_weight if total_weight > 0 else 1.0
    return {
        "success": True,
        "validator": "full_pipeline",
        "score": overall_score,
        "weight": total_weight,
        "verdict": verdict,
        "summary": {
            "total_issues": len(all_issues),
            "error_count": error_count,
            "warning_count": warning_count,
            "validators_run": len(results),
        },
        "results": [
            {
                "validator": r.validator,
                "score": r.score,
                "weight": r.weight,
                "confidence": r.confidence,
                "issues": [_format_issue(i) for i in r.issues],
                "details": r.details or {},
            }
            for r in results
        ],
        "all_issues": [
            {**_format_issue(i), "validator": r.validator}
            for r in results
            for i in r.issues
        ],
    }


def _build_validator_response(
    result: ValidationResult,
    validator_name: str,
) -> Dict[str, Any]:
    """Build standard validator response dict."""
    return {
        "success": True,
        "validator": validator_name,
        "score": result.score,
        "weight": result.weight,
        "confidence": result.confidence,
        "verdict": "pass" if result.score >= 0.8 else "review" if result.score >= 0.5 else "fail",
        "issues": [_format_issue(i) for i in result.issues],
        "details": result.details or {},
    }


def _build_error_response(
    error: Exception,
    validator_name: str,
) -> Dict[str, Any]:
    """Build error response dict for validator failures."""
    return {
        "success": False,
        "error": str(error),
        "validator": validator_name,
        "score": 0.0,
        "verdict": "error"
    }


def validate_syntax(code: str, language: str = "python", filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Multi-language syntax checking using vallm SyntaxValidator.
    
    Args:
        code: Source code to validate
        language: Programming language (python, javascript, go, rust, etc.)
        filename: Optional filename for context
        
    Returns:
        Dict with validation results including score, issues, and verdict
    """
    try:
        proposal = Proposal(
            code=code,
            language=language,
            filename=filename
        )
        
        validator = SyntaxValidator()
        result = validator.validate(proposal, {})
        
        return _build_validator_response(result, "syntax")
        
    except Exception as e:
        return _build_error_response(e, "syntax")


def validate_imports(code: str, language: str = "python", filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Import resolution validation using vallm ImportValidator.
    
    Args:
        code: Source code to validate
        language: Programming language 
        filename: Optional filename for context
        
    Returns:
        Dict with validation results including score, issues, and verdict
    """
    try:
        proposal = Proposal(
            code=code,
            language=language,
            filename=filename
        )
        
        validator = ImportValidator()
        result = validator.validate(proposal, {})
        
        return _build_validator_response(result, "imports")
        
    except Exception as e:
        return _build_error_response(e, "imports")


def validate_security(code: str, language: str = "python", filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Security issue detection using vallm SecurityValidator.
    Detects eval, exec, secrets, SQL injection, command injection, etc.
    
    Args:
        code: Source code to validate
        language: Programming language
        filename: Optional filename for context
        
    Returns:
        Dict with validation results including score, issues, and verdict
    """
    try:
        proposal = Proposal(
            code=code,
            language=language,
            filename=filename
        )
        
        validator = SecurityValidator()
        result = validator.validate(proposal, {})
        
        return _build_validator_response(result, "security")
        
    except Exception as e:
        return _build_error_response(e, "security")


def validate_code(
    code: str, 
    language: str = "python", 
    filename: Optional[str] = None,
    reference_code: Optional[str] = None,
    enable_syntax: bool = True,
    enable_imports: bool = True,
    enable_security: bool = True,
    enable_complexity: bool = True,
    enable_regression: bool = False
) -> Dict[str, Any]:
    """
    Full pipeline validation combining multiple validators.
    
    Args:
        code: Source code to validate
        language: Programming language
        filename: Optional filename for context
        reference_code: Optional reference code for regression testing
        enable_syntax: Enable syntax validation
        enable_imports: Enable import validation
        enable_security: Enable security validation
        enable_complexity: Enable complexity validation
        enable_regression: Enable regression validation (requires reference_code)
        
    Returns:
        Dict with comprehensive validation results
    """
    try:
        proposal = Proposal(
            code=code,
            language=language,
            filename=filename,
            reference_code=reference_code,
        )

        results, total_score, total_weight, all_issues = _run_validators(
            proposal, enable_syntax, enable_imports, enable_security,
            enable_complexity, enable_regression, reference_code,
        )

        overall_score = total_score / total_weight if total_weight > 0 else 1.0
        error_count = sum(1 for i in all_issues if i.severity.value == "error")
        verdict = _compute_verdict(overall_score, error_count)

        return _build_pipeline_response(results, total_weight, verdict, all_issues)
        
    except Exception as e:
        return _build_error_response(e, "full_pipeline")


# MCP tool handlers - these functions match the MCP tool schema
def handle_validate_syntax(params: Dict[str, Any]) -> Dict[str, Any]:
    """MCP handler for validate_syntax tool."""
    return validate_syntax(
        code=params.get("code", ""),
        language=params.get("language", "python"),
        filename=params.get("filename")
    )


def handle_validate_imports(params: Dict[str, Any]) -> Dict[str, Any]:
    """MCP handler for validate_imports tool."""
    return validate_imports(
        code=params.get("code", ""),
        language=params.get("language", "python"),
        filename=params.get("filename")
    )


def handle_validate_security(params: Dict[str, Any]) -> Dict[str, Any]:
    """MCP handler for validate_security tool."""
    return validate_security(
        code=params.get("code", ""),
        language=params.get("language", "python"),
        filename=params.get("filename")
    )


def handle_validate_code(params: Dict[str, Any]) -> Dict[str, Any]:
    """MCP handler for validate_code tool."""
    return validate_code(
        code=params.get("code", ""),
        language=params.get("language", "python"),
        filename=params.get("filename"),
        reference_code=params.get("reference_code"),
        enable_syntax=params.get("enable_syntax", True),
        enable_imports=params.get("enable_imports", True),
        enable_security=params.get("enable_security", True),
        enable_complexity=params.get("enable_complexity", True),
        enable_regression=params.get("enable_regression", False)
    )


# Tool schema for MCP registration
TOOL_SCHEMA_VALLM = {
    "validate_syntax": {
        "name": "validate_syntax",
        "description": "Check syntax errors in code using vallm SyntaxValidator",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Source code to validate"
                },
                "language": {
                    "type": "string", 
                    "description": "Programming language (python, javascript, go, rust, etc.)",
                    "default": "python"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional filename for context"
                }
            },
            "required": ["code"]
        }
    },
    "validate_imports": {
        "name": "validate_imports",
        "description": "Validate import resolution and dependencies using vallm ImportValidator",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Source code to validate"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language",
                    "default": "python"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional filename for context"
                }
            },
            "required": ["code"]
        }
    },
    "validate_security": {
        "name": "validate_security",
        "description": "Detect security issues (eval, exec, secrets, injection attacks) using vallm SecurityValidator",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Source code to validate"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language",
                    "default": "python"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional filename for context"
                }
            },
            "required": ["code"]
        }
    },
    "validate_code": {
        "name": "validate_code",
        "description": "Run full validation pipeline (syntax + imports + security + complexity + regression) using vallm",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Source code to validate"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language",
                    "default": "python"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional filename for context"
                },
                "reference_code": {
                    "type": "string",
                    "description": "Optional reference code for regression testing"
                },
                "enable_syntax": {
                    "type": "boolean",
                    "description": "Enable syntax validation",
                    "default": True
                },
                "enable_imports": {
                    "type": "boolean",
                    "description": "Enable import validation",
                    "default": True
                },
                "enable_security": {
                    "type": "boolean",
                    "description": "Enable security validation",
                    "default": True
                },
                "enable_complexity": {
                    "type": "boolean",
                    "description": "Enable complexity validation",
                    "default": True
                },
                "enable_regression": {
                    "type": "boolean",
                    "description": "Enable regression validation (requires reference_code)",
                    "default": False
                }
            },
            "required": ["code"]
        }
    }
}

# Handler mapping for MCP server
MCP_HANDLERS = {
    "validate_syntax": handle_validate_syntax,
    "validate_imports": handle_validate_imports,
    "validate_security": handle_validate_security,
    "validate_code": handle_validate_code
}
