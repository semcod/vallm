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

import json
from typing import Any, Dict, List, Optional

from vallm.core.proposal import Proposal
from vallm.validators.syntax import SyntaxValidator
from vallm.validators.imports.wrapper import ImportValidator
from vallm.validators.security import SecurityValidator
from vallm.validators.complexity import ComplexityValidator
from vallm.validators.regression import RegressionValidator
from vallm.scoring import ValidationResult


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
        
        return {
            "success": True,
            "validator": "syntax",
            "score": result.score,
            "weight": result.weight,
            "confidence": result.confidence,
            "verdict": "pass" if result.score >= 0.8 else "review" if result.score >= 0.5 else "fail",
            "issues": [
                {
                    "message": issue.message,
                    "severity": issue.severity.value,
                    "line": issue.line,
                    "column": issue.column,
                    "rule": issue.rule
                }
                for issue in result.issues
            ],
            "details": result.details or {}
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "validator": "syntax",
            "score": 0.0,
            "verdict": "error"
        }


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
        
        return {
            "success": True,
            "validator": "imports",
            "score": result.score,
            "weight": result.weight,
            "confidence": result.confidence,
            "verdict": "pass" if result.score >= 0.8 else "review" if result.score >= 0.5 else "fail",
            "issues": [
                {
                    "message": issue.message,
                    "severity": issue.severity.value,
                    "line": issue.line,
                    "column": issue.column,
                    "rule": issue.rule
                }
                for issue in result.issues
            ],
            "details": result.details or {}
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "validator": "imports",
            "score": 0.0,
            "verdict": "error"
        }


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
        
        return {
            "success": True,
            "validator": "security",
            "score": result.score,
            "weight": result.weight,
            "confidence": result.confidence,
            "verdict": "pass" if result.score >= 0.8 else "review" if result.score >= 0.5 else "fail",
            "issues": [
                {
                    "message": issue.message,
                    "severity": issue.severity.value,
                    "line": issue.line,
                    "column": issue.column,
                    "rule": issue.rule
                }
                for issue in result.issues
            ],
            "details": result.details or {}
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "validator": "security",
            "score": 0.0,
            "verdict": "error"
        }


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
            reference_code=reference_code
        )
        
        results = []
        total_score = 0.0
        total_weight = 0.0
        all_issues = []
        
        # Syntax validation
        if enable_syntax:
            syntax_result = SyntaxValidator().validate(proposal, {})
            results.append(syntax_result)
            total_score += syntax_result.score * syntax_result.weight
            total_weight += syntax_result.weight
            all_issues.extend(syntax_result.issues)
        
        # Import validation
        if enable_imports:
            imports_result = ImportValidator().validate(proposal, {})
            results.append(imports_result)
            total_score += imports_result.score * imports_result.weight
            total_weight += imports_result.weight
            all_issues.extend(imports_result.issues)
        
        # Security validation
        if enable_security:
            security_result = SecurityValidator().validate(proposal, {})
            results.append(security_result)
            total_score += security_result.score * security_result.weight
            total_weight += security_result.weight
            all_issues.extend(security_result.issues)
        
        # Complexity validation
        if enable_complexity:
            complexity_result = ComplexityValidator().validate(proposal, {})
            results.append(complexity_result)
            total_score += complexity_result.score * complexity_result.weight
            total_weight += complexity_result.weight
            all_issues.extend(complexity_result.issues)
        
        # Regression validation
        if enable_regression and reference_code:
            regression_result = RegressionValidator().validate(proposal, {})
            results.append(regression_result)
            total_score += regression_result.score * regression_result.weight
            total_weight += regression_result.weight
            all_issues.extend(regression_result.issues)
        
        # Calculate overall score and verdict
        overall_score = total_score / total_weight if total_weight > 0 else 1.0
        error_count = sum(1 for issue in all_issues if issue.severity.value == "error")
        warning_count = sum(1 for issue in all_issues if issue.severity.value == "warning")
        
        if overall_score >= 0.8 and error_count == 0:
            verdict = "pass"
        elif overall_score >= 0.5 and error_count == 0:
            verdict = "review"
        else:
            verdict = "fail"
        
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
                "validators_run": len(results)
            },
            "results": [
                {
                    "validator": result.validator,
                    "score": result.score,
                    "weight": result.weight,
                    "confidence": result.confidence,
                    "issues": [
                        {
                            "message": issue.message,
                            "severity": issue.severity.value,
                            "line": issue.line,
                            "column": issue.column,
                            "rule": issue.rule
                        }
                        for issue in result.issues
                    ],
                    "details": result.details or {}
                }
                for result in results
            ],
            "all_issues": [
                {
                    "message": issue.message,
                    "severity": issue.severity.value,
                    "line": issue.line,
                    "column": issue.column,
                    "rule": issue.rule,
                    "validator": result.validator
                }
                for result in results
                for issue in result.issues
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "validator": "full_pipeline",
            "score": 0.0,
            "verdict": "error"
        }


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
