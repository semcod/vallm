# Example 7: Multi-Language Validation

This example demonstrates vallm's support for **8+ programming languages** with automatic language detection.

## What It Demonstrates

- **Automatic language detection** from file paths and extensions
- **Validation of 8 languages**: Python, JavaScript, TypeScript, Go, Rust, Java, C, Ruby
- **Good vs bad code samples** — correct behavior across all languages
- **Language categorization** (compiled vs scripting vs web)

## Supported Languages

| Language | Extension | Category | Complexity via Lizard |
|----------|-----------|----------|----------------------|
| Python | `.py` | Scripting | ✓ |
| JavaScript | `.js` | Web/Scripting | ✓ |
| TypeScript | `.ts` | Web/Scripting | ✓ |
| Go | `.go` | Compiled | ✓ |
| Rust | `.rs` | Compiled | ✓ |
| Java | `.java` | Compiled | ✓ |
| C | `.c` | Compiled | ✓ |
| Ruby | `.rb` | Scripting | ✓ |

Plus 20+ more languages via tree-sitter!

## Running the Example

```bash
cd examples/07_multi_language
python main.py
```

## Expected Output

```
============================================================
Multi-Language Validation Results
============================================================

--- Good Code Samples ---
✓ python       | pass     | score: 1.00
✓ javascript   | pass     | score: 1.00
✓ typescript   | pass     | score: 1.00
✓ go           | pass     | score: 1.00
✓ rust         | pass     | score: 1.00
✓ java         | pass     | score: 1.00
✓ c            | pass     | score: 1.00
✓ ruby         | pass     | score: 1.00

--- Bad Code Samples (should fail) ---
✓ python       | fail     | score: 0.00 (expected: fail)
✓ javascript   | fail     | score: 0.00 (expected: fail)
✓ go           | fail     | score: 0.00 (expected: fail)

FINAL SUMMARY
Good code samples: 8/8 passed
Bad code samples:  3/3 correctly failed
```

## How Language Detection Works

```python
from vallm import detect_language, Language

# From file path
lang = detect_language("script.py")  # → Language.PYTHON

# From extension
lang = detect_language(".rs")  # → Language.RUST

# From language name
lang = detect_language("typescript")  # → Language.TYPESCRIPT

# Access properties
print(lang.display_name)  # "TypeScript"
print(lang.extension)     # ".ts"
print(lang.tree_sitter_id)  # "typescript"
print(lang.is_compiled)   # False
print(lang.is_web)        # True
```

## CLI with Auto-Detection

```bash
# Auto-detects Python from .py extension
vallm validate --file script.py

# Auto-detects Rust from .rs extension  
vallm check main.rs

# Validate multiple files with different languages
vallm batch src/*.py src/*.js src/*.go --recursive

# Mix languages in batch
vallm batch project/ --include "*.py,*.js,*.ts,*.go,*.rs" --recursive
```

## Using the Language Enum

```python
from vallm import Language

# Check if language is compiled
if Language.GO.is_compiled:
    print("Go requires compilation")

# Get all web languages
web_langs = [lang for lang in Language if lang.is_web]

# Get all supported languages
all_langs = list(Language)
```

## Extending Language Support

To add a new language, edit `src/vallm/core/languages.py`:

```python
class Language(Enum):
    # Existing languages...
    
    # New language
    ZIG = ("zig", ".zig", "Zig")  # tree-sitter-id, extension, display name
```

The language will be automatically:
- Detectable from file extensions
- Usable in CLI with auto-detection
- Supported in batch validation

## Analysis Output

After running, check `.vallm/multilang_summary.json` for structured results:

```json
[
  {
    "language": "python",
    "verdict": "pass",
    "score": 1.0,
    "errors": 0,
    "warnings": 0,
    "is_bad": false
  },
  ...
]
```
