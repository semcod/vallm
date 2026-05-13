"""Example 1: Basic Python code validation using vallm's default pipeline.

Demonstrates: syntax, import, and complexity validation (Tier 1 & 2).
"""

# Good code — should PASS
good_code = """
def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    if n == 1:
        return [0]
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i - 1] + fib[i - 2])
    return fib
"""

# Bad code — has syntax error, should FAIL
bad_code = """
def broken_function(x, y)
    return x + y
"""

# Complex code — should get warnings
complex_code = """
def overly_complex(a, b, c, d, e, f, g):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            if g > 0:
                                return a + b + c + d + e + f + g
                            else:
                                return a + b + c + d + e + f
                        else:
                            return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0
"""


def main():
    from examples.utils import run_validation_examples, save_analysis_data

    all_results = run_validation_examples(
        example_name="semantic_review",
        good_code=good_code,
        bad_code=bad_code,
        complex_code=complex_code,
    )

    # Save all analysis data
    save_analysis_data("semantic_review", all_results)
    for name, data in all_results.items():
        print(f"{name}: {data['verdict']} (score: {data['score']:.2f})")


if __name__ == "__main__":
    main()
