"""Example 7: Comprehensive multi-language validation.

Demonstrates: Auto-detection and validation of 8+ programming languages.
"""

import json
from pathlib import Path
from vallm import Proposal, validate, VallmSettings, Language, detect_language


# Sample code snippets in various languages
CODE_SAMPLES = {
    "python": '''
def factorial(n: int) -> int:
    """Calculate factorial with proper type hints."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
''',
    
    "javascript": '''
function factorial(n) {
    // Calculate factorial recursively
    if (n < 0) {
        throw new Error("n must be non-negative");
    }
    if (n === 0 || n === 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

module.exports = { factorial };
''',
    
    "typescript": '''
function factorial(n: number): number {
    // Calculate factorial with type safety
    if (n < 0) {
        throw new Error("n must be non-negative");
    }
    if (n === 0 || n === 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

export { factorial };
''',
    
    "go": '''
package math

import "fmt"

// Factorial calculates n! recursively
func Factorial(n int) (int, error) {
    if n < 0 {
        return 0, fmt.Errorf("n must be non-negative")
    }
    if n == 0 || n == 1 {
        return 1, nil
    }
    prev, _ := Factorial(n - 1)
    return n * prev, nil
}
''',
    
    "rust": '''
/// Calculate factorial with error handling
pub fn factorial(n: i64) -> Result<i64, String> {
    if n < 0 {
        return Err("n must be non-negative".to_string());
    }
    if n == 0 || n == 1 {
        return Ok(1);
    }
    match factorial(n - 1) {
        Ok(prev) => Ok(n * prev),
        Err(e) => Err(e),
    }
}
''',
    
    "java": '''
public class MathUtils {
    /**
     * Calculate factorial recursively
     * @param n non-negative integer
     * @return n!
     * @throws IllegalArgumentException if n < 0
     */
    public static long factorial(int n) {
        if (n < 0) {
            throw new IllegalArgumentException("n must be non-negative");
        }
        if (n == 0 || n == 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
}
''',
    
    "c": '''
#include <stdio.h>
#include <stdlib.h>

/**
 * Calculate factorial recursively
 */
long factorial(int n) {
    if (n < 0) {
        fprintf(stderr, "n must be non-negative\\n");
        exit(1);
    }
    if (n == 0 || n == 1) {
        return 1;
    }
    return n * factorial(n - 1);
}
''',
    
    "ruby": '''
# Calculate factorial with proper error handling
def factorial(n)
  raise ArgumentError, "n must be non-negative" if n < 0
  return 1 if n == 0 || n == 1
  n * factorial(n - 1)
end
''',
}


BAD_CODE_SAMPLES = {
    "python": '''
def bad(n)
    if n < 0
        return None
    result = 1
    for i in range(1, n):
        result *= i
    return result
''',  # Missing colon after if

    "javascript": '''
function bad(n) {
    if (n < 0
        return null;
    }
    return n * bad(n - 1);
}
''',  # Missing closing paren in if

    "go": '''
package main

func Bad(n int) int {
    if n < 0 {
        return 0
    }
    return n * Bad(n - 1  // Missing closing paren
}
''',
}


def test_language_detection():
    """Test automatic language detection from various sources."""
    print("=" * 60)
    print("Language Detection Tests")
    print("=" * 60)
    
    test_cases = [
        ("script.py", "Python"),
        ("app.js", "JavaScript"),
        ("main.ts", "TypeScript"),
        ("server.go", "Go"),
        ("lib.rs", "Rust"),
        ("Main.java", "Java"),
        ("program.c", "C"),
        ("test.rb", "Ruby"),
        ("config.yaml", "YAML"),
        (".py", None),  # Just extension
        ("python", "Python"),  # By name
    ]
    
    for source, expected in test_cases:
        lang = detect_language(source)
        detected = lang.display_name if lang else "None"
        status = "✓" if detected == expected else "✗"
        print(f"  {status} {source:15} → {detected:15} (expected: {expected})")
    
    print()


def validate_single_language(lang_name: str, code: str, is_bad: bool = False) -> dict:
    """Validate a single language code sample."""
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=(lang_name == "python"),  # Only Python has import validation
        enable_complexity=True,
        enable_security=False,
        enable_semantic=False,
    )
    
    proposal = Proposal(code=code, language=lang_name)
    result = validate(proposal, settings)
    
    return {
        "language": lang_name,
        "verdict": result.verdict.value,
        "score": result.weighted_score,
        "errors": result.error_count,
        "warnings": result.warning_count,
        "is_bad": is_bad,
    }


def validate_all_languages():
    """Validate all language samples."""
    print("=" * 60)
    print("Multi-Language Validation Results")
    print("=" * 60)
    
    results = []
    
    # Good code samples
    print("\n--- Good Code Samples ---")
    for lang_name, code in CODE_SAMPLES.items():
        result = validate_single_language(lang_name, code)
        results.append(result)
        
        icon = "✓" if result["verdict"] == "pass" else "⚠" if result["verdict"] == "review" else "✗"
        print(f"{icon} {lang_name:12} | {result['verdict']:8} | score: {result['score']:.2f}")
    
    # Bad code samples (should fail)
    print("\n--- Bad Code Samples (should fail) ---")
    for lang_name, code in BAD_CODE_SAMPLES.items():
        result = validate_single_language(lang_name, code, is_bad=True)
        results.append(result)
        
        # For bad code, we WANT it to fail
        expected = "fail"
        got = result["verdict"]
        icon = "✓" if got == expected else "✗"
        print(f"{icon} {lang_name:12} | {got:8} | score: {result['score']:.2f} (expected: {expected})")
    
    return results


def save_results(results: list[dict]):
    """Save validation results."""
    vallm_dir = Path(".vallm")
    vallm_dir.mkdir(exist_ok=True)
    
    summary_file = vallm_dir / "multilang_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {summary_file}")


def print_language_info():
    """Print supported languages info."""
    print("=" * 60)
    print("Supported Languages")
    print("=" * 60)
    
    categories = {
        "Compiled": [],
        "Scripting": [],
        "Web": [],
        "Data/Config": [],
    }
    
    for lang in Language:
        if lang.is_compiled:
            categories["Compiled"].append(lang.display_name)
        elif lang.is_scripting:
            categories["Scripting"].append(lang.display_name)
        elif lang.is_web:
            categories["Web"].append(lang.display_name)
        else:
            categories["Data/Config"].append(lang.display_name)
    
    for category, langs in categories.items():
        if langs:
            print(f"\n{category}:")
            for name in sorted(langs):
                print(f"  • {name}")
    
    print(f"\nTotal: {len(list(Language))} languages supported")
    print()


def main():
    """Main example function."""
    print_language_info()
    test_language_detection()
    results = validate_all_languages()
    save_results(results)
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    good_results = [r for r in results if not r["is_bad"]]
    bad_results = [r for r in results if r["is_bad"]]
    
    good_passed = sum(1 for r in good_results if r["verdict"] == "pass")
    bad_failed = sum(1 for r in bad_results if r["verdict"] == "fail")
    
    print(f"Good code samples: {good_passed}/{len(good_results)} passed")
    print(f"Bad code samples:  {bad_failed}/{len(bad_results)} correctly failed")
    
    if good_passed == len(good_results) and bad_failed == len(bad_results):
        print("\n🎉 All validations behaved as expected!")
    else:
        print("\n⚠️  Some validations did not behave as expected")


if __name__ == "__main__":
    main()
