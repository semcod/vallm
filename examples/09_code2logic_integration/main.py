"""Example 9: Integration with code2logic for logical code analysis.

Demonstrates: Using code2logic to extract logical structures and vallm to validate.
"""

import json
from pathlib import Path

try:
    from code2logic import analyze_control_flow, extract_functions
    from code2logic.visualize import generate_dot
    CODE2LOGIC_AVAILABLE = True
except ImportError:
    CODE2LOGIC_AVAILABLE = False
    print("⚠️  code2logic not installed. Run: pip install code2logic")

from vallm import Proposal, validate, VallmSettings
from vallm.core.languages import Language, detect_language
from vallm.core.graph_builder import build_python_graph


# Sample code with complex control flow
SAMPLE_CODE = '''
"""Order processing system with complex logic."""
from typing import Optional
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

def process_order(order: dict) -> OrderStatus:
    """Process order with complex business logic."""
    if not order:
        raise ValueError("Order cannot be empty")
    
    if order.get("status") == "cancelled":
        return OrderStatus.CANCELLED
    
    # Check payment
    if not order.get("paid"):
        if order.get("total", 0) == 0:
            # Free order, auto-approve
            order["paid"] = True
        else:
            return OrderStatus.PENDING
    
    # Check inventory
    items = order.get("items", [])
    for item in items:
        if item.get("quantity", 0) > item.get("stock", 0):
            # Backorder
            item["backordered"] = True
    
    # All checks passed
    if all(not item.get("backordered") for item in items):
        return OrderStatus.SHIPPED
    else:
        return OrderStatus.PAID

def calculate_discount(order: dict) -> float:
    """Calculate discount based on order value and customer status."""
    total = order.get("total", 0)
    customer_type = order.get("customer_type", "regular")
    
    if customer_type == "vip":
        if total > 1000:
            return total * 0.20  # 20% for VIP large orders
        else:
            return total * 0.10  # 10% for VIP regular orders
    elif customer_type == "premium":
        if total > 500:
            return total * 0.15
        return total * 0.05
    else:
        # Regular customer
        if total > 200:
            return total * 0.05
        return 0.0
'''


def analyze_with_code2logic(code: str) -> dict:
    """Analyze code control flow using code2logic."""
    if not CODE2LOGIC_AVAILABLE:
        return {"error": "code2logic not available"}
    
    print("=" * 60)
    print("Analyzing with code2logic...")
    print("=" * 60)
    
    try:
        # Extract functions
        functions = extract_functions(code)
        print(f"Found {len(functions)} functions:")
        for func in functions:
            print(f"  - {func['name']} ({func.get('complexity', 'N/A')} branches)")
        
        # Analyze control flow
        flow_results = []
        for func in functions:
            flow = analyze_control_flow(code, func['name'])
            flow_results.append({
                'function': func['name'],
                'branches': len(flow.get('branches', [])),
                'loops': len(flow.get('loops', [])),
                'conditions': len(flow.get('conditions', [])),
            })
        
        return {
            "functions": functions,
            "control_flow": flow_results,
        }
    except Exception as e:
        return {"error": str(e)}


def validate_with_vallm(code: str) -> dict:
    """Validate code quality with vallm."""
    print("\n" + "=" * 60)
    print("Validating with vallm...")
    print("=" * 60)
    
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
        enable_semantic=False,
    )
    
    proposal = Proposal(
        code=code,
        language="python",
        filename="order_processor.py"
    )
    
    result = validate(proposal, settings)
    
    print(f"\nVerdict: {result.verdict.value}")
    print(f"Score: {result.weighted_score:.2f}")
    print("\nValidator results:")
    for r in result.results:
        icon = "✓" if r.score >= 0.8 else "⚠" if r.score >= 0.5 else "✗"
        print(f"  {icon} {r.validator}: {r.score:.2f}")
        for issue in r.issues:
            print(f"      - {issue.message}")
    
    return {
        "verdict": result.verdict.value,
        "score": result.weighted_score,
        "errors": result.error_count,
        "warnings": result.warning_count,
        "validators": [
            {
                "name": r.validator,
                "score": r.score,
                "issues": len(r.issues)
            }
            for r in result.results
        ]
    }


def build_call_graph(code: str) -> dict:
    """Build call graph using vallm's graph builder."""
    print("\n" + "=" * 60)
    print("Building call graph...")
    print("=" * 60)
    
    graph = build_python_graph(code, "order_module")
    
    print(f"Functions: {graph.functions}")
    print(f"Classes: {graph.classes}")
    print(f"Imports: {[(e.source_module, e.imported_name) for e in graph.imports]}")
    print(f"Calls: {[(e.caller, e.callee) for e in graph.calls]}")
    
    return {
        "functions": graph.functions,
        "classes": graph.classes,
        "imports": len(graph.imports),
        "calls": len(graph.calls),
    }


def generate_report(code2logic_result: dict, vallm_result: dict, graph_result: dict, output_path: Path) -> None:
    """Generate combined analysis report."""
    report = {
        "tools": {
            "code2logic": CODE2LOGIC_AVAILABLE,
            "vallm": True,
        },
        "analysis": {
            "logical_structure": code2logic_result,
            "quality_validation": vallm_result,
            "call_graph": graph_result,
        },
        "recommendations": []
    }
    
    # Generate recommendations
    if vallm_result.get("errors", 0) > 0:
        report["recommendations"].append("Fix syntax errors before deployment")
    
    if vallm_result.get("score", 1.0) < 0.8:
        report["recommendations"].append("Review code quality issues")
    
    if graph_result.get("calls", 0) > 10:
        report["recommendations"].append("High coupling detected - consider refactoring")
    
    if code2logic_result.get("functions"):
        high_complexity = [
            f for f in code2logic_result["functions"]
            if f.get("complexity", 0) > 10
        ]
        if high_complexity:
            report["recommendations"].append(
                f"Simplify {len(high_complexity)} high-complexity functions"
            )
    
    # Save report
    report_file = output_path / ".vallm" / "code2logic_integration_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Report saved to {report_file}")
    
    # Print recommendations
    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   - {rec}")
    else:
        print("\n🎉 No issues found! Code is ready for deployment.")


def visualize_flow(code: str, output_path: Path) -> None:
    """Generate control flow visualization."""
    if not CODE2LOGIC_AVAILABLE:
        return
    
    try:
        from code2logic.visualize import generate_dot
        
        dot_content = generate_dot(code)
        dot_file = output_path / ".vallm" / "control_flow.dot"
        dot_file.write_text(dot_content)
        
        print(f"\n📈 Control flow graph saved to {dot_file}")
        print("   Render with: dot -Tpng control_flow.dot -o flow.png")
    except Exception as e:
        print(f"\n⚠️  Could not generate visualization: {e}")


def main():
    """Main example function."""
    example_dir = Path(__file__).parent
    
    print("🚀 code2logic + vallm Integration Example")
    print("=" * 60)
    print("\nAnalyzing complex order processing logic...\n")
    
    # Analyze with code2logic
    if CODE2LOGIC_AVAILABLE:
        code2logic_result = analyze_with_code2logic(SAMPLE_CODE)
    else:
        print("⚠️  code2logic not available, skipping logical analysis")
        code2logic_result = {"note": "code2logic not installed"}
    
    # Validate with vallm
    vallm_result = validate_with_vallm(SAMPLE_CODE)
    
    # Build call graph
    graph_result = build_call_graph(SAMPLE_CODE)
    
    # Generate report
    generate_report(code2logic_result, vallm_result, graph_result, example_dir)
    
    # Try to visualize
    visualize_flow(SAMPLE_CODE, example_dir)
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Quality Score: {vallm_result['score']:.2f}/1.0")
    print(f"Verdict: {vallm_result['verdict'].upper()}")
    print(f"Functions: {graph_result['functions']}")
    print(f"Complexity Issues: {vallm_result['warnings']}")


if __name__ == "__main__":
    main()
