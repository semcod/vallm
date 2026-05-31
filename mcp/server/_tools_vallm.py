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
    overall_score = (
        sum(r.score * r.weight for r in results) / total_weight if total_weight > 0 else 1.0
    )
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
            {**_format_issue(i), "validator": r.validator} for r in results for i in r.issues
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
        "verdict": "error",
    }


def create_proposal(code: str, language: str, filename: Optional[str]) -> Proposal:
    """Create a Proposal object from code, language, and filename."""
    return Proposal(code=code, language=language, filename=filename)


def compute_overall_score_and_verdict(
    results: List[ValidationResult], all_issues: List
) -> tuple[float, str]:
    """Compute overall score and verdict from validation results and issues."""
    total_weight = sum(r.weight for r in results)
    overall_score = (
        sum(r.score * r.weight for r in results) / total_weight if total_weight > 0 else 1.0
    )
    error_count = sum(1 for i in all_issues if i.severity.value == "error")
    verdict = _compute_verdict(overall_score, error_count)
    return overall_score, verdict


def validate_syntax(
    code: str, language: str = "python", filename: Optional[str] = None
) -> Dict[str, Any]:
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
        proposal = create_proposal(code, language, filename)

        validator = SyntaxValidator()
        result = validator.validate(proposal, {})

        return _build_validator_response(result, "syntax")

    except Exception as e:
        return _build_error_response(e, "syntax")


def validate_imports(
    code: str, language: str = "python", filename: Optional[str] = None
) -> Dict[str, Any]:
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
        proposal = create_proposal(code, language, filename)

        validator = ImportValidator()
        result = validator.validate(proposal, {})

        return _build_validator_response(result, "imports")

    except Exception as e:
        return _build_error_response(e, "imports")


def validate_security(
    code: str, language: str = "python", filename: Optional[str] = None
) -> Dict[str, Any]:
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
        proposal = create_proposal(code, language, filename)

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
    enable_regression: bool = False,
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
        enable_regression: Enable regression validation

    Returns:
        Dict with full pipeline validation results
    """
    try:
        proposal = create_proposal(code, language, filename)

        results, _, total_weight, all_issues = _run_validators(
            proposal,
            enable_syntax,
            enable_imports,
            enable_security,
            enable_complexity,
            enable_regression,
            reference_code,
        )

        overall_score, verdict = compute_overall_score_and_verdict(results, all_issues)

        return _build_pipeline_response(
            results,
            total_weight,
            verdict,
            all_issues,
        )

    except Exception as e:
        return _build_error_response(e, "full_pipeline")


def validate_intent_contracts(
    code: str,
    filename: str | None = None,
) -> Dict[str, Any]:
    """Validate inline @intract contracts in a code snippet."""
    try:
        from intract.integrations.vallm import validate_proposal

        mapped = validate_proposal(code, filename=filename)
        return {
            "success": True,
            "validator": "intract",
            "score": mapped.score,
            "verdict": mapped.status,
            "issues": [issue.__dict__ for issue in mapped.issues],
        }
    except ImportError:
        return {
            "success": False,
            "validator": "intract",
            "error": "Intract is not installed. Install with: pip install 'vallm[intract]'",
            "score": 0.0,
            "verdict": "error",
        }
    except Exception as e:
        return _build_error_response(e, "intract")


def validate_intract_project(
    path: str,
    manifest: str | None = None,
    staged: bool = False,
    changed: bool = False,
    base: str = "main",
) -> Dict[str, Any]:
    """Validate Intract contracts for a project directory."""
    try:
        from pathlib import Path

        from vallm.validators.intract import run_project_intract_check

        report, decision, files = run_project_intract_check(
            Path(path),
            staged=staged,
            changed=changed,
            base_ref=base,
            manifest=Path(manifest) if manifest else None,
        )
        return {
            "success": not decision.should_fail,
            "validator": "intract_project",
            "verdict": "fail" if decision.should_fail else "pass",
            "report": report.to_dict(),
            "policy": {
                "should_fail": decision.should_fail,
                "reasons": decision.reasons,
                "warnings": decision.warnings,
            },
            "changed_files": files,
        }
    except ImportError:
        return {
            "success": False,
            "validator": "intract_project",
            "error": "Intract is not installed. Install with: pip install 'vallm[intract]'",
            "verdict": "error",
        }
    except Exception as e:
        return _build_error_response(e, "intract_project")


def _call_validate_syntax(args: Dict[str, Any]) -> Dict[str, Any]:
    return validate_syntax(args.get("code", ""), args.get("language", "python"), args.get("filename"))


def _call_validate_imports(args: Dict[str, Any]) -> Dict[str, Any]:
    return validate_imports(args.get("code", ""), args.get("language", "python"), args.get("filename"))


def _call_validate_security(args: Dict[str, Any]) -> Dict[str, Any]:
    return validate_security(args.get("code", ""), args.get("language", "python"), args.get("filename"))


def _call_validate_code(args: Dict[str, Any]) -> Dict[str, Any]:
    return validate_code(
        args.get("code", ""),
        args.get("language", "python"),
        args.get("filename"),
        args.get("reference_code"),
        bool(args.get("enable_syntax", True)),
        bool(args.get("enable_imports", True)),
        bool(args.get("enable_security", True)),
        bool(args.get("enable_complexity", True)),
        bool(args.get("enable_regression", False)),
    )


def _call_validate_intent_contracts(args: Dict[str, Any]) -> Dict[str, Any]:
    return validate_intent_contracts(args.get("code", ""), args.get("filename"))


def validate_intract_staged(
    path: str,
    manifest: str | None = None,
    base: str = "main",
) -> Dict[str, Any]:
    """Validate staged Intract contracts for a project directory."""
    return validate_intract_project(path, manifest=manifest, staged=True, changed=False, base=base)


def _call_validate_intract_staged(args: Dict[str, Any]) -> Dict[str, Any]:
    return validate_intract_staged(args.get("path", "."), args.get("manifest"), args.get("base", "main"))


def _call_validate_intract_project(args: Dict[str, Any]) -> Dict[str, Any]:
    return validate_intract_project(
        args.get("path", "."),
        args.get("manifest"),
        bool(args.get("staged", False)),
        bool(args.get("changed", False)),
        args.get("base", "main"),
    )


_CODE_SCHEMA = {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Source code to validate"},
        "language": {"type": "string", "default": "python", "description": "Programming language"},
        "filename": {"type": "string", "description": "Optional filename for context"},
    },
    "required": ["code"],
}


TOOL_SCHEMA_VALLM = {
    "validate_syntax": {
        "name": "validate_syntax",
        "description": "Multi-language syntax checking using vallm SyntaxValidator",
        "parameters": _CODE_SCHEMA,
    },
    "validate_imports": {
        "name": "validate_imports",
        "description": "Import resolution validation using vallm ImportValidator",
        "parameters": _CODE_SCHEMA,
    },
    "validate_security": {
        "name": "validate_security",
        "description": "Security issue detection using vallm SecurityValidator",
        "parameters": _CODE_SCHEMA,
    },
    "validate_code": {
        "name": "validate_code",
        "description": "Full pipeline validation combining multiple validators",
        "parameters": {
            "type": "object",
            "properties": {
                **_CODE_SCHEMA["properties"],
                "reference_code": {"type": "string", "description": "Reference code for regression testing"},
                "enable_syntax": {"type": "boolean", "default": True},
                "enable_imports": {"type": "boolean", "default": True},
                "enable_security": {"type": "boolean", "default": True},
                "enable_complexity": {"type": "boolean", "default": True},
                "enable_regression": {"type": "boolean", "default": False},
            },
            "required": ["code"],
        },
    },
    "validate_intent_contracts": {
        "name": "validate_intent_contracts",
        "description": "Validate inline @intract intent contracts in a code snippet",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Source code containing @intract contracts"},
                "filename": {"type": "string", "description": "Optional filename for contract context"},
            },
            "required": ["code"],
        },
    },
    "validate_intract_project": {
        "name": "validate_intract_project",
        "description": "Validate Intract intent contracts for a project directory",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root directory", "default": "."},
                "manifest": {"type": "string", "description": "Path to intract.yaml / intent.yaml"},
                "staged": {"type": "boolean", "default": False, "description": "Validate staged files only"},
                "changed": {"type": "boolean", "default": False, "description": "Validate branch diff only"},
                "base": {"type": "string", "default": "main", "description": "Base ref for --changed"},
            },
            "required": ["path"],
        },
    },
    "validate_intract_staged": {
        "name": "validate_intract_staged",
        "description": "Validate staged Intract intent contracts before commit",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root directory", "default": "."},
                "manifest": {"type": "string", "description": "Path to intract.yaml / intent.yaml"},
                "base": {"type": "string", "default": "main", "description": "Unused compatibility field"},
            },
            "required": ["path"],
        },
    },
}


MCP_HANDLERS = {
    "validate_syntax": _call_validate_syntax,
    "validate_imports": _call_validate_imports,
    "validate_security": _call_validate_security,
    "validate_code": _call_validate_code,
    "validate_intent_contracts": _call_validate_intent_contracts,
    "validate_intract_project": _call_validate_intract_project,
    "validate_intract_staged": _call_validate_intract_staged,
}
