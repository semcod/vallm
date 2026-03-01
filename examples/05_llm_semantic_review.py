"""Example 5: LLM-as-judge semantic review with Ollama.

Demonstrates: Using a local Ollama model (Qwen 2.5 Coder 7B) for code review.

Prerequisites:
    1. Install Ollama: https://ollama.com
    2. Pull the model: ollama pull qwen2.5-coder:7b
    3. Install ollama package: pip install ollama
"""

from vallm import Proposal, VallmSettings, validate

# Code with subtle bug (off-by-one error)
buggy_code = """
def binary_search(arr: list[int], target: int) -> int:
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid
        else:
            right = mid
    return -1
"""

# Correct implementation for reference
correct_code = """
def binary_search(arr: list[int], target: int) -> int:
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""

# Code that works but has poor practices
poor_practices = """
import os, sys, json, re

def f(d):
    r = []
    for k in d:
        v = d[k]
        if type(v) == str:
            r.append(v.upper())
        elif type(v) == int:
            r.append(str(v))
        elif type(v) == list:
            for i in v:
                r.append(str(i))
    return r
"""


def main():
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
        enable_semantic=True,
        llm_provider="ollama",
        llm_model="qwen2.5-coder:7b",
        llm_base_url="http://localhost:11434",
    )

    print("=" * 60)
    print("LLM Review: Buggy binary search (with reference)")
    print("=" * 60)
    proposal = Proposal(
        code=buggy_code,
        language="python",
        reference_code=correct_code,
        filename="search.py",
    )
    result = validate(proposal, settings)
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    for r in result.results:
        print(f"\n  [{r.validator}] score={r.score:.2f}")
        if r.details.get("scores"):
            for k, v in r.details["scores"].items():
                print(f"    {k}: {v:.2f}")
        if r.details.get("summary"):
            print(f"    Summary: {r.details['summary']}")
        for issue in r.issues:
            print(f"    {issue}")

    print("\n" + "=" * 60)
    print("LLM Review: Poor practices code")
    print("=" * 60)
    proposal = Proposal(
        code=poor_practices,
        language="python",
        filename="utils.py",
    )
    result = validate(proposal, settings)
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    for r in result.results:
        print(f"\n  [{r.validator}] score={r.score:.2f}")
        if r.details.get("scores"):
            for k, v in r.details["scores"].items():
                print(f"    {k}: {v:.2f}")
        if r.details.get("summary"):
            print(f"    Summary: {r.details['summary']}")
        for issue in r.issues:
            print(f"    {issue}")


if __name__ == "__main__":
    main()
