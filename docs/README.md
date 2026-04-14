---
path: /home/tom/github/semcod/vallm
---

<!-- code2docs:start --># vallm

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-425-green)
> **425** functions | **44** classes | **102** files | CC̄ = 3.5

> Auto-generated project documentation from source code analysis.

**Author:** semcod  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/semcod/vallm](https://github.com/semcod/vallm)

### From PyPI

```bash
pip install vallm
```

### From Source

```bash
git clone https://github.com/semcod/vallm
cd vallm
pip install -e .
```

### Optional Extras

```bash
pip install vallm[security]    # security features
pip install vallm[semantic]    # semantic features
pip install vallm[llm]    # LLM integration (litellm)
pip install vallm[graph]    # graph features
pip install vallm[docker]    # docker features
pip install vallm[all]    # all optional features
pip install vallm[dev]    # development tools
```

# Only regenerate README
vallm ./my-project --readme-only

# Preview what would be generated (no file writes)
vallm ./my-project --dry-run

# Check documentation health
vallm check ./my-project

# Sync — regenerate only changed modules
vallm sync ./my-project
```

### Python API

```python
from vallm import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```

## Generated Output

When you run `vallm`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `vallm.yaml` in your project root (or run `vallm init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

vallm can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- vallm:start -->
# Project Title
... auto-generated content ...
<!-- vallm:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

```
vallm/
├── project    ├── run├── mcp_server        ├── main_template        ├── main        ├── run        ├── docker-entrypoint├── examples/        ├── main        ├── main        ├── run            ├── data_processor        ├── iteration_1        ├── docker-entrypoint        ├── best_version        ├── iteration_2            ├── simple_buggy            ├── process_user_input            ├── load_config        ├── utils/        ├── ollama_simple_demo            ├── calculate_total            ├── main            ├── save_data        ├── main        ├── claude_autonomous_demo        ├── main_template        ├── main        ├── main        ├── run        ├── docker-entrypoint        ├── main        ├── refactored_output        ├── main            ├── order_processor        ├── extraction        ├── save_analysis_data    ├── utils/        ├── extract_code_from_response        ├── mcp_demo        ├── logging_utils        ├── validation_runner        ├── hookspecs        ├── cli/    ├── mcp_demo    ├── vallm/        ├── __main__            ├── file_cache        ├── main            ├── complexity            ├── base            ├── logical            ├── regression        ├── validators/            ├── security            ├── semantic_cache            ├── syntax            ├── lint            ├── imports/            ├── semantic                ├── base                ├── javascript_imports                ├── python_imports                ├── go_imports                ├── c_imports                ├── rust_imports                ├── wrapper                ├── factory                ├── utils                ├── java_imports            ├── graph_diff        ├── core/            ├── proposal            ├── gitignore        ├── scoring            ├── ast_compare            ├── batch_constants            ├── batch_processor_patterns            ├── batch_processor_files            ├── batch_utils            ├── batch_processor_validation            ├── output_formatters/            ├── batch_processor_impl            ├── batch_processor                ├── base                ├── shared                ├── utils                ├── single            ├── languages                ├── batch        ├── sandbox/    ├── bump_version├── mcp/    ├── server/            ├── runner        ├── _tools_vallm        ├── self_server        ├── config            ├── command_handlers```

### Classes

- **`DataProcessor`** — Data processor with multiple responsibilities - violates SRP.
- **`ReportGenerator`** — Report generator with tight coupling to DataProcessor.
- **`BadClass`** — Class with multiple issues.
- **`Colors`** — —
- **`Colors`** — —
- **`OrderManager`** — Class with single responsibility - adheres to SOLID principles.
- **`OrderManager`** — Class with mixed responsibilities - SOLID violation.
- **`Colors`** — —
- **`Colors`** — ANSI color codes for terminal output.
- **`VallmSpec`** — Hook specifications that validators must implement.
- **`FileValidationCache`** — In-memory cache keyed on file path + mtime + size.
- **`ComplexityValidator`** — Tier 2: Cyclomatic complexity, maintainability index, and function metrics.
- **`BaseValidator`** — Base class for all vallm validators.
- **`LogicalErrorValidator`** — Validator for logical errors using pyflakes.
- **`RegressionValidator`** — Tier 2: Run pytest against proposed code and report pass/fail.
- **`SecurityValidator`** — Tier 2: Security analysis using built-in patterns and optionally bandit.
- **`SemanticCache`** — Cache for semantic validation results to improve performance.
- **`SyntaxValidator`** — Tier 1: Fast syntax validation.
- **`LintValidator`** — Validator for linting issues using ruff.
- **`SemanticValidator`** — Tier 3: LLM-as-judge semantic code review.
- **`BaseImportValidator`** — Base class for all import validators.
- **`JavaScriptImportValidator`** — JavaScript/TypeScript import validator.
- **`PythonImportValidator`** — Python-specific import validator.
- **`GoImportValidator`** — Go import validator.
- **`CImportValidator`** — C/C++ import validator.
- **`RustImportValidator`** — Rust import validator.
- **`ImportValidator`** — Backward compatibility wrapper for the refactored import validation system.
- **`ImportValidatorFactory`** — Factory for creating language-specific import validators.
- **`JavaImportValidator`** — Java import validator.
- **`GraphDiffResult`** — Result of comparing two code graphs.
- **`Proposal`** — A code proposal to be validated.
- **`GitignoreParser`** — Parse .gitignore files and match paths against patterns.
- **`Verdict`** — —
- **`Severity`** — —
- **`Issue`** — A single issue found during validation.
- **`ValidationResult`** — Result from a single validator.
- **`PipelineResult`** — Aggregated result from all validators.
- **`CompiledPatterns`** — —
- **`BatchProcessor`** — Handles batch validation of multiple files.
- **`Language`** — Supported programming languages with their tree-sitter identifiers.
- **`ExecutionResult`** — Result of sandboxed code execution.
- **`SandboxRunner`** — Unified interface for running code in a sandbox.
- **`VallmSettings`** — vallm configuration with layered sources: defaults → TOML → env → CLI.

### Functions

- `run_example()` — —
- `main()` — —
- `main()` — —
- `print_section()` — —
- `print_step()` — —
- `print_success()` — —
- `print_warning()` — —
- `print_error()` — —
- `analyze_with_code2logic(code)` — Analyze code control flow using code2logic.
- `validate_with_vallm(code)` — Validate code quality with vallm.
- `build_call_graph(code)` — Build call graph using vallm's graph builder.
- `generate_report(code2logic_result, vallm_result, graph_result, output_path)` — Generate combined analysis report.
- `visualize_flow(code, output_path)` — Generate control flow visualization.
- `main()` — Main example function.
- `main()` — —
- `load_config()` — Load configuration - security issue with eval.
- `init_database()` — Initialize database connection.
- `main()` — Main function with multiple issues.
- `main()` — Main function with improvements.
- `main()` — Main function with improvements.
- `main()` — Main function with improvements.
- `process_user_input(user_input)` — Process user input with security issues.
- `load_config()` — Load configuration with eval.
- `save_data(data, filename)` — Save data without validation.
- `calculate_total(items)` — Calculate total with no error handling.
- `duplicate_function()` — Another duplicate function.
- `unused_function()` — This function is never used.
- `main()` — Main function with problems.
- `process_user_input(user_input)` — Process user input with standard logic.
- `load_config()` — Load configuration with default values.
- `log_section(title)` — —
- `log_step(step, description)` — —
- `analyze_with_code2llm(code_path)` — Simple code2llm analysis.
- `call_ollama(prompt, model)` — Call Ollama API.
- `validate_with_vallm(code)` — Simple vallm validation.
- `run_simple_test(code)` — Simple syntax test.
- `generate_ollama_prompt(code, analysis)` — Generate simple prompt for Ollama.
- `run_simple_workflow(code_path, max_iterations)` — Run simple refactoring workflow.
- `main()` — Main function.
- `calculate_total(items)` — Calculate total price from items list.
- `run_demo_main()` — Run the standard demo main function pattern.
- `save_data(data, filename)` — Save data to JSON file.
- `main()` — —
- `log_section(title)` — Print a section header.
- `log_step(step, description)` — Print a step.
- `log_code(label, code, max_lines)` — Log code with label.
- `analyze_with_code2llm(code_path)` — Analyze code structure and smells using code2llm.
- `call_claude_code(prompt, model, temperature)` — Call Claude Code API.
- `validate_with_vallm(code, description)` — Validate code using vallm.
- `run_runtime_tests(code_path, test_file)` — Run runtime tests on the refactored code.
- `create_basic_tests(code_path, test_file)` — Create basic tests for the code.
- `generate_claude_prompt(code, analysis, iteration)` — Generate comprehensive prompt for Claude Code.
- `generate_feedback_prompt(current_code, validation, test_results, analysis)` — Generate feedback prompt for Claude based on validation and test results.
- `run_autonomous_workflow(code_path, max_iterations)` — Run the complete autonomous refactoring workflow.
- `main()` — Main entry point.
- `main()` — —
- `main()` — —
- `main()` — —
- `print_section()` — —
- `print_step()` — —
- `print_success()` — —
- `print_warning()` — —
- `print_error()` — —
- `print()` — —
- `main()` — —
- `validate_email(email)` — Email validation using regex.
- `calculate_shipping(weight)` — Calculate shipping cost with constants.
- `load_config()` — Load config securely using json.loads.
- `save_data(data, filename)` — Save data safely using json.dump.
- `process_order(data)` — Process order data with proper error handling and validation.
- `main()` — —
- `test_language_detection()` — Test automatic language detection from various sources.
- `validate_single_language(lang_name, code, is_bad)` — Validate a single language code sample.
- `validate_all_languages()` — Validate all language samples.
- `save_results(results)` — Save validation results.
- `print_language_info()` — Print supported languages info.
- `main()` — Main example function.
- `process_order(data)` — Process order data - has multiple issues.
- `load_config()` — Load config - security issue with eval.
- `save_data(data, filename)` — Save data - uses pickle without validation.
- `calculate(x, y, z, a)` — Too many parameters - maintainability issue.
- `validate_email_1(email)` — Email validation - duplicated logic.
- `validate_email_2(email)` — Email validation - same logic, different function.
- `calculate_shipping(weight)` — Calculate shipping with magic numbers.
- `dead_code()` — Function that's never called.
- `extract_code_from_response(response, language)` — Extract code from LLM response.
- `extract_json_from_response(response)` — Extract JSON object from LLM response.
- `save_analysis_data(example_name, result_data)` — Save analysis data to JSON file.
- `save_analysis_data(example_name, result_data)` — Save analysis data to .vallm folder.
- `run_validation_examples(example_name, good_code, bad_code, complex_code)` — Run standard validation examples (good, bad, complex code).
- `validate_code_example(name, code, settings, all_results)` — Validate a code example and store results.
- `print_summary(all_results)` — Print summary of all validation results.
- `extract_code_from_response(response)` — Extract Python code from LLM response.
- `log_section(title)` — Print a section header.
- `log_step(step, description)` — Print a step.
- `log_code(label, code, max_lines)` — Log code with label.
- `analyze_with_code2llm(code_path)` — Analyze code structure using code2llm.
- `validate_with_vallm(code, description)` — Validate code using vallm.
- `call_ollama(prompt, model, temperature)` — Call Ollama API.
- `generate_refactoring_prompt(code, analysis)` — Generate prompt for LLM to refactor code.
- `run_mcp_workflow(code_path, max_iterations)` — Run the complete MCP workflow.
- `main()` — Main entry point.
- `log_section(title)` — Print a section header.
- `log_step(step, description)` — Print a step indicator.
- `log_code(label, code, max_lines)` — Log code with label and truncation.
- `log_result(status, message)` — Log a result with appropriate color.
- `run_validation_examples(example_name, good_code, bad_code, complex_code)` — Run standard validation examples (good, bad, complex code).
- `example_syntax_validation()` — Example: Syntax validation for multiple languages.
- `example_security_validation()` — Example: Security vulnerability detection.
- `example_full_pipeline()` — Example: Full validation pipeline.
- `example_selective_validation()` — Example: Selective validator usage.
- `main()` — Run all examples.
- `get_file_cache()` — —
- `clear_file_cache()` — —
- `create_sample_project(base_path)` — Create a sample project for analysis.
- `analyze_with_code2llm(project_path)` — Analyze project structure using code2llm.
- `validate_with_vallm(project_path)` — Validate all Python files with vallm.
- `generate_report(code2llm_result, vallm_result, output_path)` — Generate combined analysis report.
- `main()` — Main example function.
- `create_validator(settings)` — Factory function for LogicalErrorValidator.
- `get_semantic_cache()` — Get global semantic cache instance.
- `clear_semantic_cache()` — Clear global semantic cache.
- `create_validator(settings)` — Factory function for LintValidator.
- `walk(root, project_root, gitignore_matcher, skip_tests)` — Walk directory tree yielding Python files.
- `validate_import_path(import_path, source_file, project_root, known_modules)` — Validate if an import path is resolvable.
- `diff_graphs(before, after)` — Compare two CodeGraphs and return the diff.
- `diff_python_code(before_code, after_code)` — Convenience function: build graphs from code strings and diff them.
- `load_gitignore(path)` — Load .gitignore from a directory.
- `get_default_excludes()` — Get default exclude patterns used when no .gitignore exists.
- `create_default_gitignore_parser()` — Create a parser with default exclude patterns.
- `should_exclude(path, gitignore_parser, use_defaults)` — Check if a path should be excluded.
- `compute_verdict(results, settings, filename)` — Compute the aggregate verdict from a list of validation results.
- `validate(proposal, settings, validators, context)` — Run the full validation pipeline on a proposal.
- `parse_code(code, language)` — Parse code using tree-sitter and return the tree.
- `parse_python_ast(code)` — Parse Python code using the built-in ast module. Returns None on failure.
- `normalize_python_ast(tree)` — Normalize a Python AST by replacing identifiers with canonical names.
- `python_ast_similarity(code1, code2)` — Compute structural similarity between two Python code snippets.
- `tree_sitter_node_count(code, language)` — Count the number of nodes in a tree-sitter parse tree.
- `tree_sitter_error_count(code, language)` — Count syntax errors reported by tree-sitter.
- `structural_diff_summary(code1, code2, language)` — Return a summary of structural differences between two code snippets.
- `parse_filter_patterns(include, exclude)` — Parse include and exclude patterns into compiled matchers.
- `matches_pattern(path, compiled)` — Check whether a path matches compiled patterns.
- `should_exclude_file(path, exclude_patterns)` — Return True if the file should be excluded.
- `matches_include_pattern(path, include_patterns)` — Return True if the file matches include patterns.
- `filter_files(files, include, exclude, gitignore_parser)` — Filter files based on patterns and gitignore.
- `build_file_list(paths, recursive)` — Build list of files from input paths.
- `compile_patterns(raw)` — —
- `validate_single_file(file_path, settings)` — Validate a single file (top-level for thread-pool compatibility).
- `process_files(files, settings, output_format, fail_fast)` — Validate files concurrently and aggregate results.
- `output_validate_result(result, output_format, verbose)` — Output validation result in the specified format.
- `output_batch_results(results_by_language, filtered_files, passed_count, failed_files)` — Output batch validation results in the specified format.
- `output_batch_empty(output_format)` — Output empty results.
- `output_json(result)` — Output single file validation result as JSON (used by validate command).
- `output_text(result)` — Output single file validation result as text (used by validate command).
- `output_rich(result, verbose)` — Output rich formatted validation result.
- `output_batch_rich(results_by_language, filtered_files, passed_count, failed_files)` — Output rich formatted batch summary.
- `output_batch_text(results_by_language, filtered_files, passed_count, failed_files)` — Output plain text batch summary.
- `format_error_message(error)` — Format error messages consistently across all output formats.
- `build_files_data(results_by_language)` — Build standardized files data structure for all output formats.
- `build_failed_files_data(failed_files)` — Build standardized failed files data structure for all output formats.
- `output_batch_json(results_by_language, filtered_files, passed_count, failed_files)` — Output JSON batch summary with detailed per-file results.
- `output_batch_yaml(results_by_language, filtered_files, passed_count, failed_files)` — Output YAML batch summary with detailed per-file results.
- `output_batch_toon(results_by_language, filtered_files, passed_count, failed_files)` — Output TOON format batch summary with detailed per-file results.
- `print_summary_header()` — Print summary header for batch results.
- `build_results_table(results_by_language)` — Build results table for rich output.
- `output_validate_result(result, output_format, verbose)` — —
- `output_batch_results(results_by_language, filtered_files, passed_count, failed_files)` — —
- `format_error_message(error)` — Format error messages consistently across all output formats.
- `build_files_data(results_by_language)` — Build standardized files data structure for all output formats.
- `build_failed_files_data(failed_files)` — Build standardized failed files data structure for all output formats.
- `format_error_message(error)` — —
- `build_files_data(results_by_language)` — —
- `build_failed_files_data(failed_files)` — —
- `output_json(result)` — Output single file validation result as JSON (used by validate command).
- `output_text(result)` — Output single file validation result as text (used by validate command).
- `output_rich(result, verbose)` — Output rich formatted validation result.
- `detect_language(source)` — Auto-detect language from file path, extension, or name.
- `get_language_for_validation(source, explicit)` — Get tree-sitter language ID for validation.
- `output_batch_results(results_by_language, filtered_files, passed_count, failed_files)` — Output batch validation results in the specified format.
- `output_batch_empty(output_format)` — Output empty results.
- `output_batch_rich(results_by_language, filtered_files, passed_count, failed_files)` — Output rich formatted batch summary.
- `output_batch_text(results_by_language, filtered_files, passed_count, failed_files)` — Output plain text batch summary.
- `output_batch_json(results_by_language, filtered_files, passed_count, failed_files)` — Output batch results as JSON.
- `output_batch_yaml(results_by_language, filtered_files, passed_count, failed_files)` — Output batch results as YAML-like text.
- `output_batch_toon(results_by_language, filtered_files, passed_count, failed_files)` — Output TOON format batch summary with detailed per-file results.
- `print_summary_header()` — Print a standard header for batch summaries.
- `build_results_table(results_by_language)` — Build a rich table for batch results.
- `bump_version(version_str, bump_type)` — Bump version string based on type.
- `main()` — —
- `validate_syntax(code, language, filename)` — Multi-language syntax checking using vallm SyntaxValidator.
- `validate_imports(code, language, filename)` — Import resolution validation using vallm ImportValidator.
- `validate_security(code, language, filename)` — Security issue detection using vallm SecurityValidator.
- `validate_code(code, language, filename, reference_code)` — Full pipeline validation combining multiple validators.
- `handle_validate_syntax(params)` — MCP handler for validate_syntax tool.
- `handle_validate_imports(params)` — MCP handler for validate_imports tool.
- `handle_validate_security(params)` — MCP handler for validate_security tool.
- `handle_validate_code(params)` — MCP handler for validate_code tool.
- `handle_initialize(request_id)` — Handle MCP initialize request.
- `handle_tools_list(request_id)` — Handle tools/list request - return available vallm tools.
- `handle_tools_call(request_id, params)` — Handle tools/call request - execute vallm validation.
- `handle_request(request)` — Handle incoming MCP request.
- `main()` — Main MCP server loop.
- `get_settings()` — Get global settings instance, loading from .env if available.
- `reload_settings()` — Reload settings from environment variables.
- `get_default_filenames()` — Get default output filenames by format.
- `get_default_output_format()` — Get default output format.
- `get_default_language()` — Get default programming language.
- `validate_command(code, file, language, reference)` — Validate code with the full pipeline.
- `check_command(code, file, language, output_format)` — Quick syntax check only (tier 1).
- `batch_command(paths, recursive, include, exclude)` — Validate multiple files with auto-detected languages.
- `info_command(language, clear_cache)` — Show information about supported languages and validators.


## Project Structure

📦 `examples`
📄 `examples.01_basic_validation.main` (1 functions)
📄 `examples.02_ast_comparison.main` (1 functions)
📄 `examples.03_security_check.main` (1 functions)
📄 `examples.04_graph_analysis.main` (1 functions)
📄 `examples.05_llm_semantic_review.main` (1 functions)
📄 `examples.05_llm_semantic_review.main_template` (1 functions)
📄 `examples.06_multilang_validation.main` (1 functions)
📄 `examples.06_multilang_validation.main_template` (1 functions)
📄 `examples.07_multi_language.main` (6 functions)
📄 `examples.08_code2llm_integration.main` (5 functions)
📄 `examples.09_code2logic_integration.main` (6 functions)
📄 `examples.10_mcp_ollama_demo.docker-entrypoint`
📄 `examples.10_mcp_ollama_demo.legacy_code.order_processor` (14 functions, 1 classes)
📄 `examples.10_mcp_ollama_demo.mcp_demo` (9 functions, 1 classes)
📄 `examples.10_mcp_ollama_demo.refactored_output` (13 functions, 1 classes)
📄 `examples.10_mcp_ollama_demo.run` (9 functions)
📄 `examples.11_claude_code_autonomous.claude_autonomous_demo` (12 functions, 1 classes)
📄 `examples.11_claude_code_autonomous.docker-entrypoint`
📄 `examples.11_claude_code_autonomous.legacy_code.data_processor` (16 functions, 2 classes)
📄 `examples.11_claude_code_autonomous.run` (5 functions)
📄 `examples.12_ollama_simple_demo.best_version` (1 functions)
📄 `examples.12_ollama_simple_demo.docker-entrypoint`
📄 `examples.12_ollama_simple_demo.iteration_1` (1 functions)
📄 `examples.12_ollama_simple_demo.iteration_2` (1 functions)
📄 `examples.12_ollama_simple_demo.legacy_code.simple_buggy` (11 functions, 1 classes)
📄 `examples.12_ollama_simple_demo.ollama_simple_demo` (9 functions, 1 classes)
📄 `examples.12_ollama_simple_demo.run`
📦 `examples.12_ollama_simple_demo.utils`
📄 `examples.12_ollama_simple_demo.utils.calculate_total` (1 functions)
📄 `examples.12_ollama_simple_demo.utils.load_config` (1 functions)
📄 `examples.12_ollama_simple_demo.utils.main` (1 functions)
📄 `examples.12_ollama_simple_demo.utils.process_user_input` (1 functions)
📄 `examples.12_ollama_simple_demo.utils.save_data` (1 functions)
📄 `examples.mcp_demo` (5 functions)
📄 `examples.run` (1 functions)
📦 `examples.utils` (4 functions)
📄 `examples.utils.extract_code_from_response` (1 functions)
📄 `examples.utils.extraction` (2 functions)
📄 `examples.utils.logging_utils` (4 functions, 1 classes)
📄 `examples.utils.save_analysis_data` (1 functions)
📄 `examples.utils.validation_runner` (1 functions)
📦 `mcp`
📦 `mcp.server`
📄 `mcp.server._tools_vallm` (14 functions)
📄 `mcp.server.self_server` (5 functions)
📄 `mcp_server`
📄 `project`
📄 `scripts.bump_version` (2 functions)
📦 `src.vallm`
📄 `src.vallm.__main__`
📦 `src.vallm.cli`
📄 `src.vallm.cli.batch_constants`
📄 `src.vallm.cli.batch_processor`
📄 `src.vallm.cli.batch_processor_files` (1 functions)
📄 `src.vallm.cli.batch_processor_impl` (21 functions, 1 classes)
📄 `src.vallm.cli.batch_processor_patterns` (7 functions, 1 classes)
📄 `src.vallm.cli.batch_processor_validation` (2 functions)
📄 `src.vallm.cli.batch_utils` (1 functions, 1 classes)
📄 `src.vallm.cli.command_handlers` (11 functions)
📦 `src.vallm.cli.output_formatters` (3 functions)
📄 `src.vallm.cli.output_formatters.base` (2 functions)
📄 `src.vallm.cli.output_formatters.batch` (16 functions)
📄 `src.vallm.cli.output_formatters.shared` (4 functions)
📄 `src.vallm.cli.output_formatters.single` (3 functions)
📄 `src.vallm.cli.output_formatters.utils` (3 functions)
📄 `src.vallm.config` (6 functions, 1 classes)
📦 `src.vallm.core`
📄 `src.vallm.core.ast_compare` (8 functions)
📄 `src.vallm.core.gitignore` (10 functions, 1 classes)
📄 `src.vallm.core.graph_diff` (3 functions, 1 classes)
📄 `src.vallm.core.languages` (6 functions, 1 classes)
📄 `src.vallm.core.proposal` (1 classes)
📄 `src.vallm.hookspecs` (3 functions, 1 classes)
📦 `src.vallm.sandbox`
📄 `src.vallm.sandbox.runner` (4 functions, 2 classes)
📄 `src.vallm.scoring` (8 functions, 5 classes)
📦 `src.vallm.validators`
📄 `src.vallm.validators.base` (1 functions, 1 classes)
📄 `src.vallm.validators.complexity` (4 functions, 1 classes)
📄 `src.vallm.validators.file_cache` (7 functions, 1 classes)
📦 `src.vallm.validators.imports`
📄 `src.vallm.validators.imports.base` (7 functions, 1 classes)
📄 `src.vallm.validators.imports.c_imports` (4 functions, 1 classes)
📄 `src.vallm.validators.imports.factory` (3 functions, 1 classes)
📄 `src.vallm.validators.imports.go_imports` (5 functions, 1 classes)
📄 `src.vallm.validators.imports.java_imports` (5 functions, 1 classes)
📄 `src.vallm.validators.imports.javascript_imports` (7 functions, 1 classes)
📄 `src.vallm.validators.imports.python_imports` (9 functions, 1 classes)
📄 `src.vallm.validators.imports.rust_imports` (5 functions, 1 classes)
📄 `src.vallm.validators.imports.utils` (5 functions)
📄 `src.vallm.validators.imports.wrapper` (1 functions, 1 classes)
📄 `src.vallm.validators.lint` (6 functions, 1 classes)
📄 `src.vallm.validators.logical` (5 functions, 1 classes)
📄 `src.vallm.validators.regression` (10 functions, 1 classes)
📄 `src.vallm.validators.security` (5 functions, 1 classes)
📄 `src.vallm.validators.semantic` (15 functions, 1 classes)
📄 `src.vallm.validators.semantic_cache` (8 functions, 1 classes)
📄 `src.vallm.validators.syntax` (3 functions, 1 classes)

## Requirements

- Python >= >=3.10
- pluggy >=1.6- pydantic >=2.12- pydantic-settings >=2.13- typer >=0.24- rich >=14.3- tree-sitter >=0.25- tree-sitter-language-pack >=1.4- radon >=6.0- lizard >=1.21- pyflakes >=3.4

## Contributing

**Contributors:**
- Tom Sapletta

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

# Clone the repository
git clone https://github.com/semcod/vallm
cd vallm

# Install in development mode
pip install -e ".[dev]"

## Documentation

- 📖 [Full Documentation](https://github.com/semcod/vallm/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/semcod/vallm/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/semcod/vallm/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/semcod/vallm/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](https://github.com/wronai/vallm/blob/main/docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](https://github.com/wronai/vallm/blob/main/docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](https://github.com/wronai/vallm/blob/main/docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](https://github.com/wronai/vallm/blob/main/docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](https://github.com/wronai/vallm/blob/main/docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](https://github.com/wronai/vallm/blob/main/docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](https://github.com/wronai/vallm/blob/main/docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](https://github.com/wronai/vallm/blob/main/docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](./CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->