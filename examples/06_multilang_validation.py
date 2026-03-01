"""Example 6: Multi-language code validation.

Demonstrates: Validating JavaScript, C, and TypeScript code using tree-sitter.
"""

from vallm import Proposal, VallmSettings, validate

js_good = """
function quickSort(arr) {
    if (arr.length <= 1) return arr;
    const pivot = arr[Math.floor(arr.length / 2)];
    const left = arr.filter(x => x < pivot);
    const middle = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);
    return [...quickSort(left), ...middle, ...quickSort(right)];
}
"""

js_bad = """
function quickSort(arr) {
    if (arr.length <= 1) return arr
    const pivot = arr[Math.floor(arr.length / 2)]
    const left = arr.filter(x => x < pivot
    const right = arr.filter(x => x > pivot);
    return [...quickSort(left), ...quickSort(right)];
}
"""

c_good = """
#include <stdio.h>

int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}
"""

c_bad = """
#include <stdio.h>

int gcd(int a, int b) {
    while (b != 0) {
        int temp = b
        b = a % b;
        a = temp;
    }
    return a;
"""


def main():
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=False,
        enable_complexity=True,
        enable_security=False,
        enable_semantic=False,
    )

    examples = [
        ("JavaScript (good)", js_good, "javascript"),
        ("JavaScript (bad)", js_bad, "javascript"),
        ("C (good)", c_good, "c"),
        ("C (bad)", c_bad, "c"),
    ]

    for label, code, language in examples:
        print("=" * 60)
        print(f"Validating: {label}")
        print("=" * 60)
        proposal = Proposal(code=code, language=language)
        result = validate(proposal, settings)
        print(f"Verdict: {result.verdict.value}")
        print(f"Score:   {result.weighted_score:.2f}")
        for r in result.results:
            print(f"  {r.validator}: score={r.score:.2f}")
            for issue in r.issues:
                print(f"    {issue}")
        print()


if __name__ == "__main__":
    main()
