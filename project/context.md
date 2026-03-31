# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/vallm
- **Primary Language**: python
- **Languages**: python: 79, shell: 8
- **Analysis Mode**: static
- **Total Functions**: 369
- **Total Classes**: 41
- **Modules**: 87
- **Entry Points**: 236

## Architecture by Module

### src.vallm.cli.output_formatters
- **Functions**: 24
- **File**: `output_formatters.py`

### src.vallm.cli.batch_processor
- **Functions**: 17
- **Classes**: 1
- **File**: `batch_processor.py`

### examples.11_claude_code_autonomous.legacy_code.data_processor
- **Functions**: 16
- **Classes**: 2
- **File**: `data_processor.py`

### src.vallm.validators.semantic
- **Functions**: 15
- **Classes**: 1
- **File**: `semantic.py`

### examples.10_mcp_ollama_demo.legacy_code.order_processor
- **Functions**: 14
- **Classes**: 1
- **File**: `order_processor.py`

### examples.10_mcp_ollama_demo.refactored_output
- **Functions**: 13
- **Classes**: 1
- **File**: `refactored_output.py`

### examples.11_claude_code_autonomous.claude_autonomous_demo
- **Functions**: 12
- **Classes**: 1
- **File**: `claude_autonomous_demo.py`

### mcp.server._tools_vallm
- **Functions**: 12
- **File**: `_tools_vallm.py`

### examples.12_ollama_simple_demo.legacy_code.simple_buggy
- **Functions**: 11
- **Classes**: 1
- **File**: `simple_buggy.py`

### src.vallm.cli.command_handlers
- **Functions**: 11
- **File**: `command_handlers.py`

### src.vallm.validators.regression
- **Functions**: 10
- **Classes**: 1
- **File**: `regression.py`

### src.vallm.core.gitignore
- **Functions**: 10
- **Classes**: 1
- **File**: `gitignore.py`

### examples.12_ollama_simple_demo.ollama_simple_demo
- **Functions**: 9
- **Classes**: 1
- **File**: `ollama_simple_demo.py`

### examples.10_mcp_ollama_demo.run
- **Functions**: 9
- **File**: `run.sh`

### examples.10_mcp_ollama_demo.mcp_demo
- **Functions**: 9
- **Classes**: 1
- **File**: `mcp_demo.py`

### src.vallm.validators.semantic_cache
- **Functions**: 8
- **Classes**: 1
- **File**: `semantic_cache.py`

### src.vallm.scoring
- **Functions**: 8
- **Classes**: 5
- **File**: `scoring.py`

### src.vallm.validators.imports.base
- **Functions**: 7
- **Classes**: 1
- **File**: `base.py`

### src.vallm.validators.imports.javascript_imports
- **Functions**: 7
- **Classes**: 1
- **File**: `javascript_imports.py`

### src.vallm.validators.imports.python_imports
- **Functions**: 7
- **Classes**: 1
- **File**: `python_imports.py`

## Key Entry Points

Main execution flows into the system:

### examples.04_graph_analysis.main.main
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, build_python_graph, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print

### examples.utils.validation_runner.run_validation_examples
> Run standard validation examples (good, bad, complex code).

Args:
    example_name: Name for saving analysis data
    good_code: Example of good code
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, Proposal, src.vallm.validators.base.BaseValidator.validate, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print

### examples.11_claude_code_autonomous.claude_autonomous_demo.main
> Main entry point.
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.parse_args, Path, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print

### examples.02_ast_comparison.main.main
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, src.vallm.core.ast_compare.python_ast_similarity, src.vallm.core.ast_compare.python_ast_similarity, src.vallm.core.ast_compare.python_ast_similarity, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print

### src.vallm.cli.command_handlers.batch_command
> Validate multiple files with auto-detected languages.
- **Calls**: typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### examples.05_llm_semantic_review.main.main
- **Calls**: VallmSettings, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, Proposal, src.vallm.validators.base.BaseValidator.validate, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print

### examples.12_ollama_simple_demo.ollama_simple_demo.main
> Main function.
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.parse_args, Path, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.12_ollama_simple_demo.ollama_simple_demo.run_simple_workflow

### examples.03_security_check.main.main
- **Calls**: SecurityValidator, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, Proposal, validator.validate, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print

### examples.10_mcp_ollama_demo.mcp_demo.main
> Main entry point.
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.parse_args, Path, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.mcp_demo.run_mcp_workflow

### src.vallm.cli.command_handlers.validate_command
> Validate code with the full pipeline.
- **Calls**: typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.extract_imports
> Extract import statements from JavaScript/TypeScript using tree-sitter.
- **Calls**: get_parser, parser.parse, src.vallm.validators.imports.utils.walk, code.encode, enumerate, src.vallm.validators.imports.utils.walk, re.finditer, imports.append

### examples.09_code2logic_integration.main.main
> Main example function.
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.09_code2logic_integration.main.validate_with_vallm, examples.09_code2logic_integration.main.build_call_graph, examples.09_code2logic_integration.main.generate_report, examples.09_code2logic_integration.main.visualize_flow, examples.10_mcp_ollama_demo.run.print

### src.vallm.validators.imports.go_imports.GoImportValidator.extract_imports
> Extract import statements from Go using tree-sitter.
- **Calls**: get_parser, parser.parse, src.vallm.validators.imports.utils.walk, code.encode, re.finditer, src.vallm.validators.imports.utils.walk, imports.append, child.child_by_field_name

### scripts.bump_version.main
- **Calls**: pyproject_path.read_text, re.search, version_match.group, scripts.bump_version.bump_version, re.sub, pyproject_path.write_text, examples.10_mcp_ollama_demo.run.print, len

### examples.07_multi_language.main.main
> Main example function.
- **Calls**: examples.07_multi_language.main.print_language_info, examples.07_multi_language.main.test_language_detection, examples.07_multi_language.main.validate_all_languages, examples.07_multi_language.main.save_results, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, sum

### src.vallm.validators.lint.LintValidator._parse_ruff_result
> Parse a ruff JSON result into an Issue.

Args:
    item: Ruff result dictionary
    
Returns:
    Issue object
- **Calls**: any, Issue, None.startswith, None.startswith, item.get, None.get, None.get, None.get

### src.vallm.validators.imports.rust_imports.RustImportValidator.extract_imports
> Extract use statements from Rust using tree-sitter.
- **Calls**: get_parser, parser.parse, src.vallm.validators.imports.utils.walk, code.encode, re.finditer, src.vallm.validators.imports.utils.walk, None.strip, imports.append

### src.vallm.cli.output_formatters.output_batch_text
> Output plain text batch summary.
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print

### src.vallm.cli.batch_processor.BatchProcessor._process_files
> Process all files for validation.
- **Calls**: len, enumerate, self._show_progress, self._read_file_text, self._detect_file_language, Proposal, src.vallm.validators.base.BaseValidator.validate, self._handle_validation_result

### src.vallm.core.gitignore.GitignoreParser._pattern_to_regex
> Convert a gitignore pattern to a regex pattern.
- **Calls**: len, None.join, result.append, result.append, result.append, len, pattern.find, result.append

### examples.mcp_demo.main
> Run all examples.
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.mcp_demo.example_syntax_validation, examples.mcp_demo.example_security_validation, examples.mcp_demo.example_full_pipeline, examples.mcp_demo.example_selective_validation, examples.10_mcp_ollama_demo.run.print

### src.vallm.validators.lint.LintValidator._parse_ruff_text
> Parse ruff text output as fallback.

Args:
    output: Ruff text output
    
Returns:
    List of Issue objects
- **Calls**: None.split, line.strip, output.strip, line.split, len, int, int, message.startswith

### mcp.server.self_server.main
> Main MCP server loop.
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, line.strip, examples.10_mcp_ollama_demo.run.print, json.loads, mcp.server.self_server.handle_request, examples.10_mcp_ollama_demo.run.print, json.dumps

### examples.utils.validate_code_example
> Validate a code example and store results.

Args:
    name: Example name identifier
    code: Code string to validate
    settings: VallmSettings inst
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, Proposal, src.vallm.validators.base.BaseValidator.validate, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print

### examples.08_code2llm_integration.main.main
> Main example function.
- **Calls**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.08_code2llm_integration.main.create_sample_project, examples.10_mcp_ollama_demo.run.print, examples.08_code2llm_integration.main.validate_with_vallm, examples.08_code2llm_integration.main.generate_report, examples.10_mcp_ollama_demo.run.print

### src.vallm.validators.security.SecurityValidator.validate
- **Calls**: self._check_patterns, issues.extend, _LANGUAGE_PATTERNS.get, ValidationResult, self._check_patterns, issues.extend, self._check_python_ast, issues.extend

### src.vallm.sandbox.runner.SandboxRunner._run_subprocess
> Run code in a subprocess with resource limits.
- **Calls**: ext_map.get, cmd_map.get, ExecutionResult, tempfile.NamedTemporaryFile, f.write, time.monotonic, subprocess.run, ExecutionResult

### src.vallm.sandbox.runner.SandboxRunner._run_docker
> Run code in a Docker container (requires docker package).
- **Calls**: docker.from_env, image_map.get, cmd_map.get, client.containers.run, container.wait, None.decode, container.remove, ExecutionResult

### src.vallm.cli.command_handlers.info_command
> Show information about supported languages and validators.
- **Calls**: typer.Option, typer.Option, src.vallm.validators.semantic_cache.clear_semantic_cache, None.get_cache_stats, console.print, console.print, src.vallm.cli.command_handlers._show_general_info, Language

### examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.calculate_metrics
> Calculate metrics with performance issues.
- **Calls**: range, len, range, item.items, len, isinstance, len, isinstance

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [examples.04_graph_analysis.main]
  └─ →> print
  └─ →> print
```

### Flow 2: run_validation_examples
```
run_validation_examples [examples.utils.validation_runner]
  └─ →> print
  └─ →> print
  └─ →> validate
```

### Flow 3: batch_command
```
batch_command [src.vallm.cli.command_handlers]
```

### Flow 4: validate_command
```
validate_command [src.vallm.cli.command_handlers]
```

### Flow 5: extract_imports
```
extract_imports [src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator]
  └─ →> walk
      └─> _should_skip_dir
      └─> _is_gitignored
```

### Flow 6: _parse_ruff_result
```
_parse_ruff_result [src.vallm.validators.lint.LintValidator]
```

### Flow 7: output_batch_text
```
output_batch_text [src.vallm.cli.output_formatters]
  └─ →> print
  └─ →> print
```

### Flow 8: _process_files
```
_process_files [src.vallm.cli.batch_processor.BatchProcessor]
```

### Flow 9: _pattern_to_regex
```
_pattern_to_regex [src.vallm.core.gitignore.GitignoreParser]
```

## Key Classes

### src.vallm.cli.batch_processor.BatchProcessor
> Handles batch validation of multiple files.
- **Methods**: 17
- **Key Methods**: src.vallm.cli.batch_processor.BatchProcessor.__init__, src.vallm.cli.batch_processor.BatchProcessor.process_batch, src.vallm.cli.batch_processor.BatchProcessor.output_batch_results, src.vallm.cli.batch_processor.BatchProcessor._load_gitignore_parser, src.vallm.cli.batch_processor.BatchProcessor._build_file_list, src.vallm.cli.batch_processor.BatchProcessor._filter_files, src.vallm.cli.batch_processor.BatchProcessor._parse_filter_patterns, src.vallm.cli.batch_processor.BatchProcessor._should_exclude_file, src.vallm.cli.batch_processor.BatchProcessor._matches_include_pattern, src.vallm.cli.batch_processor.BatchProcessor._handle_no_files_found

### src.vallm.validators.semantic.SemanticValidator
> Tier 3: LLM-as-judge semantic code review.
- **Methods**: 15
- **Key Methods**: src.vallm.validators.semantic.SemanticValidator.__init__, src.vallm.validators.semantic.SemanticValidator.validate, src.vallm.validators.semantic.SemanticValidator._build_prompt, src.vallm.validators.semantic.SemanticValidator._call_llm, src.vallm.validators.semantic.SemanticValidator._call_ollama, src.vallm.validators.semantic.SemanticValidator._call_litellm, src.vallm.validators.semantic.SemanticValidator._call_http, src.vallm.validators.semantic.SemanticValidator._parse_response, src.vallm.validators.semantic.SemanticValidator._extract_json_from_response, src.vallm.validators.semantic.SemanticValidator._create_parse_error_result
- **Inherits**: BaseValidator

### examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor
> Data processor with multiple responsibilities - violates SRP.
- **Methods**: 10
- **Key Methods**: examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.__init__, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.process_user_data, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.calculate_metrics, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.export_data, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.validate_email, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.validate_email_again, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.process_with_external_api, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.complex_calculation, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.unused_function, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.another_unused_function

### src.vallm.validators.regression.RegressionValidator
> Tier 2: Run pytest against proposed code and report pass/fail.

The validator writes the proposed co
- **Methods**: 10
- **Key Methods**: src.vallm.validators.regression.RegressionValidator.__init__, src.vallm.validators.regression.RegressionValidator.validate, src.vallm.validators.regression.RegressionValidator._resolve_test_dir, src.vallm.validators.regression.RegressionValidator._write_code, src.vallm.validators.regression.RegressionValidator._build_pytest_cmd, src.vallm.validators.regression.RegressionValidator._run_pytest, src.vallm.validators.regression.RegressionValidator._interpret, src.vallm.validators.regression.RegressionValidator._parse_failures, src.vallm.validators.regression.RegressionValidator._timeout_result, src.vallm.validators.regression.RegressionValidator._exception_result
- **Inherits**: BaseValidator

### examples.10_mcp_ollama_demo.refactored_output.OrderManager
> Class with single responsibility - adheres to SOLID principles.
- **Methods**: 7
- **Key Methods**: examples.10_mcp_ollama_demo.refactored_output.OrderManager.__init__, examples.10_mcp_ollama_demo.refactored_output.OrderManager.add_order, examples.10_mcp_ollama_demo.refactored_output.OrderManager.validate_order, examples.10_mcp_ollama_demo.refactored_output.OrderManager.execute_query, examples.10_mcp_ollama_demo.refactored_output.OrderManager.process_payment, examples.10_mcp_ollama_demo.refactored_output.OrderManager.send_email, examples.10_mcp_ollama_demo.refactored_output.OrderManager.get_stats

### src.vallm.validators.imports.base.BaseImportValidator
> Base class for all import validators.
- **Methods**: 7
- **Key Methods**: src.vallm.validators.imports.base.BaseImportValidator.validate, src.vallm.validators.imports.base.BaseImportValidator.extract_imports, src.vallm.validators.imports.base.BaseImportValidator.module_exists, src.vallm.validators.imports.base.BaseImportValidator.get_language, src.vallm.validators.imports.base.BaseImportValidator._get_error_message, src.vallm.validators.imports.base.BaseImportValidator._get_rule_name, src.vallm.validators.imports.base.BaseImportValidator.create_validation_result
- **Inherits**: ABC

### src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator
> JavaScript/TypeScript import validator.
- **Methods**: 7
- **Key Methods**: src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.__init__, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.validate, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.extract_imports, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.module_exists, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.get_language, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator._get_error_message, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator._get_rule_name
- **Inherits**: BaseImportValidator

### src.vallm.core.languages.Language
> Supported programming languages with their tree-sitter identifiers.
- **Methods**: 7
- **Key Methods**: src.vallm.core.languages.Language.__init__, src.vallm.core.languages.Language.from_extension, src.vallm.core.languages.Language.from_path, src.vallm.core.languages.Language.from_string, src.vallm.core.languages.Language.is_compiled, src.vallm.core.languages.Language.is_scripting, src.vallm.core.languages.Language.is_web
- **Inherits**: Enum

### examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager
> Class with mixed responsibilities - SOLID violation.
- **Methods**: 6
- **Key Methods**: examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.__init__, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.add_order, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.execute_query, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.process_payment, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.send_email, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.get_stats

### src.vallm.validators.semantic_cache.SemanticCache
> Cache for semantic validation results to improve performance.
- **Methods**: 6
- **Key Methods**: src.vallm.validators.semantic_cache.SemanticCache.__init__, src.vallm.validators.semantic_cache.SemanticCache._get_cache_key, src.vallm.validators.semantic_cache.SemanticCache.get, src.vallm.validators.semantic_cache.SemanticCache.set, src.vallm.validators.semantic_cache.SemanticCache.clear, src.vallm.validators.semantic_cache.SemanticCache.get_cache_stats

### src.vallm.validators.imports.python_imports.PythonImportValidator
> Python-specific import validator.
- **Methods**: 6
- **Key Methods**: src.vallm.validators.imports.python_imports.PythonImportValidator.validate, src.vallm.validators.imports.python_imports.PythonImportValidator.extract_imports, src.vallm.validators.imports.python_imports.PythonImportValidator.module_exists, src.vallm.validators.imports.python_imports.PythonImportValidator.get_language, src.vallm.validators.imports.python_imports.PythonImportValidator._get_error_message, src.vallm.validators.imports.python_imports.PythonImportValidator._get_rule_name
- **Inherits**: BaseImportValidator

### src.vallm.core.gitignore.GitignoreParser
> Parse .gitignore files and match paths against patterns.
- **Methods**: 6
- **Key Methods**: src.vallm.core.gitignore.GitignoreParser.__init__, src.vallm.core.gitignore.GitignoreParser._parse, src.vallm.core.gitignore.GitignoreParser.matches, src.vallm.core.gitignore.GitignoreParser._match_pattern, src.vallm.core.gitignore.GitignoreParser._fnmatch, src.vallm.core.gitignore.GitignoreParser._pattern_to_regex

### src.vallm.validators.security.SecurityValidator
> Tier 2: Security analysis using built-in patterns and optionally bandit.
- **Methods**: 5
- **Key Methods**: src.vallm.validators.security.SecurityValidator.validate, src.vallm.validators.security.SecurityValidator._check_patterns, src.vallm.validators.security.SecurityValidator._check_python_ast, src.vallm.validators.security.SecurityValidator._get_func_name, src.vallm.validators.security.SecurityValidator._try_bandit
- **Inherits**: BaseValidator

### src.vallm.validators.lint.LintValidator
> Validator for linting issues using ruff.
- **Methods**: 5
- **Key Methods**: src.vallm.validators.lint.LintValidator.__init__, src.vallm.validators.lint.LintValidator.validate, src.vallm.validators.lint.LintValidator._check_ruff, src.vallm.validators.lint.LintValidator._parse_ruff_result, src.vallm.validators.lint.LintValidator._parse_ruff_text

### src.vallm.validators.imports.go_imports.GoImportValidator
> Go import validator.
- **Methods**: 5
- **Key Methods**: src.vallm.validators.imports.go_imports.GoImportValidator.get_language, src.vallm.validators.imports.go_imports.GoImportValidator._get_error_message, src.vallm.validators.imports.go_imports.GoImportValidator._get_rule_name, src.vallm.validators.imports.go_imports.GoImportValidator.extract_imports, src.vallm.validators.imports.go_imports.GoImportValidator.module_exists
- **Inherits**: BaseImportValidator

### src.vallm.validators.imports.rust_imports.RustImportValidator
> Rust import validator.
- **Methods**: 5
- **Key Methods**: src.vallm.validators.imports.rust_imports.RustImportValidator.get_language, src.vallm.validators.imports.rust_imports.RustImportValidator._get_error_message, src.vallm.validators.imports.rust_imports.RustImportValidator._get_rule_name, src.vallm.validators.imports.rust_imports.RustImportValidator.extract_imports, src.vallm.validators.imports.rust_imports.RustImportValidator.module_exists
- **Inherits**: BaseImportValidator

### src.vallm.validators.imports.java_imports.JavaImportValidator
> Java import validator.
- **Methods**: 5
- **Key Methods**: src.vallm.validators.imports.java_imports.JavaImportValidator.get_language, src.vallm.validators.imports.java_imports.JavaImportValidator._get_error_message, src.vallm.validators.imports.java_imports.JavaImportValidator._get_rule_name, src.vallm.validators.imports.java_imports.JavaImportValidator.extract_imports, src.vallm.validators.imports.java_imports.JavaImportValidator.module_exists
- **Inherits**: BaseImportValidator

### src.vallm.validators.logical.LogicalErrorValidator
> Validator for logical errors using pyflakes.
- **Methods**: 4
- **Key Methods**: src.vallm.validators.logical.LogicalErrorValidator.__init__, src.vallm.validators.logical.LogicalErrorValidator.validate, src.vallm.validators.logical.LogicalErrorValidator._check_pyflakes, src.vallm.validators.logical.LogicalErrorValidator._parse_pyflakes_line

### src.vallm.validators.complexity.ComplexityValidator
> Tier 2: Cyclomatic complexity, maintainability index, and function metrics.
- **Methods**: 4
- **Key Methods**: src.vallm.validators.complexity.ComplexityValidator.__init__, src.vallm.validators.complexity.ComplexityValidator.validate, src.vallm.validators.complexity.ComplexityValidator._check_python_complexity, src.vallm.validators.complexity.ComplexityValidator._check_lizard
- **Inherits**: BaseValidator

### src.vallm.validators.imports.c_imports.CImportValidator
> C/C++ import validator.
- **Methods**: 4
- **Key Methods**: src.vallm.validators.imports.c_imports.CImportValidator.__init__, src.vallm.validators.imports.c_imports.CImportValidator.validate, src.vallm.validators.imports.c_imports.CImportValidator.extract_imports, src.vallm.validators.imports.c_imports.CImportValidator.module_exists
- **Inherits**: BaseImportValidator

## Data Transformation Functions

Key functions that process and transform data:

### examples.09_code2logic_integration.main.validate_with_vallm
> Validate code quality with vallm.
- **Output to**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, VallmSettings, Proposal

### examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.process_user_data
> Process user data with deep nesting and security issues.
- **Output to**: isinstance, len, connection.cursor, cursor.execute, connection.commit

### examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.validate_email
> Email validation - duplicate function.

### examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.validate_email_again
> Duplicate email validation function.

### examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.process_with_external_api
> Process data with external API - no error handling.
- **Output to**: requests.get, response.json

### examples.12_ollama_simple_demo.legacy_code.simple_buggy.process_user_input
> Process user input with security issues.
- **Output to**: user_input.startswith, user_input.startswith, eval, examples.10_mcp_ollama_demo.run.print

### examples.12_ollama_simple_demo.legacy_code.simple_buggy.BadClass.process_data
> Method with no error handling.
- **Output to**: isinstance, self.data.append

### examples.12_ollama_simple_demo.utils.process_user_input.process_user_input
> Process user input with standard logic.

Args:
    user_input: Raw user input string
    
Returns:
 
- **Output to**: user_input.startswith, user_input.startswith, str, examples.10_mcp_ollama_demo.run.print, user_input.lower

### examples.12_ollama_simple_demo.ollama_simple_demo.validate_with_vallm
> Simple vallm validation.
- **Output to**: examples.12_ollama_simple_demo.ollama_simple_demo.log_step, VallmSettings, Proposal, src.vallm.validators.base.BaseValidator.validate, examples.10_mcp_ollama_demo.run.print

### examples.11_claude_code_autonomous.claude_autonomous_demo.validate_with_vallm
> Validate code using vallm.
- **Output to**: logger.info, VallmSettings, Proposal, src.vallm.validators.base.BaseValidator.validate, examples.10_mcp_ollama_demo.run.print

### examples.07_multi_language.main.validate_single_language
> Validate a single language code sample.
- **Output to**: VallmSettings, Proposal, src.vallm.validators.base.BaseValidator.validate

### examples.07_multi_language.main.validate_all_languages
> Validate all language samples.
- **Output to**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, CODE_SAMPLES.items

### examples.10_mcp_ollama_demo.refactored_output.OrderManager.validate_order
> Validate order data.

### examples.10_mcp_ollama_demo.refactored_output.OrderManager.process_payment
> Process payment securely.
- **Output to**: examples.10_mcp_ollama_demo.run.print

### examples.10_mcp_ollama_demo.refactored_output.validate_email
> Email validation using regex.
- **Output to**: re.match

### examples.10_mcp_ollama_demo.refactored_output.process_order
> Process order data with proper error handling and validation.

### examples.10_mcp_ollama_demo.legacy_code.order_processor.process_order
> Process order data - has multiple issues.
- **Output to**: len

### examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.process_payment
> Process payment - security issues.
- **Output to**: examples.10_mcp_ollama_demo.run.print

### examples.10_mcp_ollama_demo.legacy_code.order_processor.validate_email_1
> Email validation - duplicated logic.

### examples.10_mcp_ollama_demo.legacy_code.order_processor.validate_email_2
> Email validation - same logic, different function.

### examples.utils.validate_code_example
> Validate a code example and store results.

Args:
    name: Example name identifier
    code: Code s
- **Output to**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, Proposal, src.vallm.validators.base.BaseValidator.validate

### examples.10_mcp_ollama_demo.mcp_demo.validate_with_vallm
> Validate code using vallm.
- **Output to**: logger.info, VallmSettings, Proposal, src.vallm.validators.base.BaseValidator.validate, examples.10_mcp_ollama_demo.run.print

### src.vallm.hookspecs.VallmSpec.validate_proposal
> Validate a code proposal and return a ValidationResult.

### examples.08_code2llm_integration.main.validate_with_vallm
> Validate all Python files with vallm.
- **Output to**: examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, examples.10_mcp_ollama_demo.run.print, VallmSettings, project_path.rglob

### src.vallm.validators.base.BaseValidator.validate
> Validate a proposal and return a result.

## Behavioral Patterns

### recursion_walk
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: src.vallm.validators.imports.utils.walk

### recursion_output_batch_results
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: src.vallm.cli.batch_processor.BatchProcessor.output_batch_results

### state_machine_ComplexityValidator
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.vallm.validators.complexity.ComplexityValidator.__init__, src.vallm.validators.complexity.ComplexityValidator.validate, src.vallm.validators.complexity.ComplexityValidator._check_python_complexity, src.vallm.validators.complexity.ComplexityValidator._check_lizard

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `examples.11_claude_code_autonomous.claude_autonomous_demo.analyze_with_code2llm` - 43 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.run_autonomous_workflow` - 42 calls
- `examples.04_graph_analysis.main.main` - 40 calls
- `examples.utils.run_validation_examples` - 40 calls
- `examples.utils.validation_runner.run_validation_examples` - 40 calls
- `examples.10_mcp_ollama_demo.mcp_demo.analyze_with_code2llm` - 36 calls
- `examples.10_mcp_ollama_demo.mcp_demo.run_mcp_workflow` - 36 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.main` - 34 calls
- `examples.12_ollama_simple_demo.ollama_simple_demo.run_simple_workflow` - 31 calls
- `examples.02_ast_comparison.main.main` - 31 calls
- `src.vallm.cli.command_handlers.batch_command` - 30 calls
- `examples.05_llm_semantic_review.main.main` - 29 calls
- `examples.12_ollama_simple_demo.ollama_simple_demo.analyze_with_code2llm` - 29 calls
- `examples.12_ollama_simple_demo.ollama_simple_demo.main` - 29 calls
- `examples.03_security_check.main.main` - 29 calls
- `src.vallm.cli.output_formatters.output_batch_yaml` - 29 calls
- `examples.10_mcp_ollama_demo.mcp_demo.main` - 27 calls
- `src.vallm.cli.output_formatters.output_batch_toon` - 22 calls
- `src.vallm.cli.command_handlers.validate_command` - 21 calls
- `examples.08_code2llm_integration.main.generate_report` - 20 calls
- `src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.extract_imports` - 19 calls
- `examples.09_code2logic_integration.main.main` - 18 calls
- `src.vallm.validators.imports.go_imports.GoImportValidator.extract_imports` - 18 calls
- `scripts.bump_version.main` - 18 calls
- `examples.09_code2logic_integration.main.analyze_with_code2logic` - 17 calls
- `examples.09_code2logic_integration.main.generate_report` - 17 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.create_basic_tests` - 17 calls
- `examples.07_multi_language.main.main` - 17 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.run_runtime_tests` - 16 calls
- `examples.08_code2llm_integration.main.validate_with_vallm` - 16 calls
- `src.vallm.validators.imports.rust_imports.RustImportValidator.extract_imports` - 16 calls
- `src.vallm.cli.output_formatters.output_batch_text` - 16 calls
- `src.vallm.cli.output_formatters.build_results_table` - 16 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.call_claude_code` - 15 calls
- `examples.07_multi_language.main.print_language_info` - 15 calls
- `src.vallm.cli.output_formatters.output_batch_empty` - 15 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.generate_claude_prompt` - 14 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.generate_feedback_prompt` - 14 calls
- `examples.mcp_demo.main` - 14 calls
- `mcp.server.self_server.main` - 14 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> print
    main --> build_python_graph
    run_validation_examp --> print
    run_validation_examp --> Proposal
    run_validation_examp --> validate
    main --> ArgumentParser
    main --> add_argument
    main --> parse_args
    main --> Path
    main --> python_ast_similarit
    batch_command --> Argument
    batch_command --> Option
    main --> VallmSettings
    main --> Proposal
    main --> SecurityValidator
    validate_command --> Option
    extract_imports --> get_parser
    extract_imports --> parse
    extract_imports --> walk
    extract_imports --> encode
    extract_imports --> enumerate
    main --> validate_with_vallm
    main --> build_call_graph
    extract_imports --> finditer
    main --> read_text
    main --> search
    main --> group
    main --> bump_version
    main --> sub
    main --> print_language_info
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.