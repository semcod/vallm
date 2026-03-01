"""Example 2: AST comparison and structural analysis.

Demonstrates: tree-sitter parsing, Python AST normalization, similarity scoring.
"""

import json
from pathlib import Path
from vallm.core.ast_compare import (
    parse_code,
    python_ast_similarity,
    tree_sitter_node_count,
    tree_sitter_error_count,
    structural_diff_summary,
)

# Two semantically similar but syntactically different implementations
code_v1 = """
def add(a, b):
    return a + b
"""

code_v2 = """
def sum_values(x, y):
    result = x + y
    return result
"""

# Completely different code
code_v3 = """
def multiply(a, b):
    product = 1
    for _ in range(b):
        product += a
    return product
"""

# Multi-language example
js_code = """
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
"""

c_code = """
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
"""


def save_analysis_data(example_name: str, result_data: dict):
    """Save analysis data to .vallm folder."""
    vallm_dir = Path(".vallm")
    vallm_dir.mkdir(exist_ok=True)
    
    # Save result summary
    summary_file = vallm_dir / f"{example_name}_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(result_data, f, indent=2, default=str)
    
    print(f"Analysis data saved to {summary_file}")


def main():
    all_results = {}
    print("=" * 60)
    print("AST Similarity (Python)")
    print("=" * 60)

    sim_v1_v2 = python_ast_similarity(code_v1, code_v2)
    sim_v1_v3 = python_ast_similarity(code_v1, code_v3)
    sim_v2_v3 = python_ast_similarity(code_v2, code_v3)

    print(f"add() vs sum_values(): {sim_v1_v2:.3f}")
    print(f"add() vs multiply():   {sim_v1_v3:.3f}")
    # Store result data
    all_results["ast_similarity"] = {
        "sim_v1_v2": sim_v1_v2,
        "sim_v1_v3": sim_v1_v3,
        "sim_v2_v3": sim_v2_v3
    }

    print("\n" + "=" * 60)
    print("Tree-sitter Node Counts")
    print("=" * 60)

    # Store result data
    all_results["node_counts"] = {}
    for label, code, lang in [
        ("Python add()", code_v1, "python"),
        ("Python multiply()", code_v3, "python"),
        ("JavaScript fibonacci()", js_code, "javascript"),
        ("C factorial()", c_code, "c"),
    ]:
        nodes = tree_sitter_node_count(code.strip(), lang)
        errors = tree_sitter_error_count(code.strip(), lang)
        print(f"{label}: {nodes} nodes, {errors} errors")
        all_results["node_counts"][label] = {"nodes": nodes, "errors": errors}

    print("\n" + "=" * 60)
    print("Structural Diff: v1 → v2")
    print("=" * 60)

    diff = structural_diff_summary(code_v1, code_v2, "python")
    print(f"Nodes before: {diff['nodes_before']}")
    print(f"Nodes after:  {diff['nodes_after']}")
    print(f"Added types:  {diff['added_types']}")
    # Store result data
    all_results["structural_diff"] = diff

    # Save all analysis data
    save_analysis_data("ast_comparison", all_results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"AST Similarity: v1-v2={all_results['ast_similarity']['sim_v1_v2']:.3f}, v1-v3={all_results['ast_similarity']['sim_v1_v3']:.3f}")
    print(f"Node counts analyzed: {len(all_results['node_counts'])} languages")
    print(f"Structural diff: {diff['nodes_before']} → {diff['nodes_after']} nodes")


if __name__ == "__main__":
    main()
