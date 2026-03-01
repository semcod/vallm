"""Example 1: Basic Python code validation using vallm's default pipeline.

Demonstrates: syntax, import, and complexity validation (Tier 1 & 2).
"""

from vallm import Proposal, validate, VallmSettings

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
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
        enable_semantic=False,
    )

    print("=" * 60)
    print("Example 1: Validating GOOD code")
    print("=" * 60)
    proposal = Proposal(code=good_code, language="python")
    result = validate(proposal, settings)
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: score={r.score:.2f}, issues={len(r.issues)}")
    print()

    print("=" * 60)
    print("Example 2: Validating BAD code (syntax error)")
    print("=" * 60)
    proposal = Proposal(code=bad_code, language="python")
    result = validate(proposal, settings)
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: score={r.score:.2f}, issues={len(r.issues)}")
        for issue in r.issues:
            print(f"    {issue}")
    print()

    print("=" * 60)
    print("Example 3: Validating COMPLEX code")
    print("=" * 60)
    proposal = Proposal(code=complex_code, language="python")
    result = validate(proposal, settings)
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: score={r.score:.2f}, issues={len(r.issues)}")
        for issue in r.issues:
            print(f"    {issue}")


if __name__ == "__main__":
    main()
