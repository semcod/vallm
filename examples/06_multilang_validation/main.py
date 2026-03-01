"""Example 6: Multi-language code validation.

Demonstrates: Validating JavaScript, TypeScript, C, Go, Rust, and Java code using tree-sitter.
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

ts_good = """
interface User {
    id: number;
    name: string;
    email: string;
}

function greet(user: User): string {
    return `Hello, ${user.name}!`;
}

export { User, greet };
"""

ts_bad = """
interface User {
    id: number
    name: string
    email: string  // Missing semicolons

function greet(user: User): string {
    return `Hello, ${user.name}!`
// Missing closing brace
"""

go_good = """
package main

import "fmt"

func fibonacci(n int) []int {
    if n <= 0 {
        return []int{}
    }
    if n == 1 {
        return []int{0}
    }
    fib := make([]int, n)
    fib[0], fib[1] = 0, 1
    for i := 2; i < n; i++ {
        fib[i] = fib[i-1] + fib[i-2]
    }
    return fib
}

func main() {
    fmt.Println(fibonacci(10))
}
"""

go_bad = """
package main

import "fmt"

func fibonacci(n int) []int {
    if n <= 0 {
        return []int{}
    if n == 1 {  // Missing closing brace
        return []int{0}
    }
    fib := make([]int, n)
    fib[0], fib[1] = 0, 1
    for i := 2; i < n; i++ {
        fib[i] = fib[i-1] + fib[i-2]
    return fib  // Missing closing brace
"""

rust_good = """
fn factorial(n: u64) -> u64 {
    match n {
        0 => 1,
        _ => n * factorial(n - 1),
    }
}

fn main() {
    println!("Factorial of 10: {}", factorial(10));
}
"""

rust_bad = """
fn factorial(n: u64) -> u64 {
    match n {
        0 => 1,
        _ => n * factorial(n - 1),
    }
// Missing closing brace

fn main() {
    println!("Factorial of 10: {}", factorial(10));
// Missing closing brace
"""

java_good = """
public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }
    
    public static int multiply(int a, int b) {
        return a * b;
    }
    
    public static void main(String[] args) {
        System.out.println("2 + 3 = " + add(2, 3));
        System.out.println("2 * 3 = " + multiply(2, 3));
    }
}
"""

java_bad = """
public class Calculator {
    public static int add(int a, int b) {
        return a + b
    
    public static int multiply(int a, int b) {
        return a * b;
    }
// Missing closing brace
"""


def main():
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=True,
        enable_semantic=False,
    )

    examples = [
        ("JavaScript (good)", js_good, "javascript"),
        ("JavaScript (bad)", js_bad, "javascript"),
        ("TypeScript (good)", ts_good, "typescript"),
        ("TypeScript (bad)", ts_bad, "typescript"),
        ("C (good)", c_good, "c"),
        ("C (bad)", c_bad, "c"),
        ("Go (good)", go_good, "go"),
        ("Go (bad)", go_bad, "go"),
        ("Rust (good)", rust_good, "rust"),
        ("Rust (bad)", rust_bad, "rust"),
        ("Java (good)", java_good, "java"),
        ("Java (bad)", java_bad, "java"),
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
