# System Architecture Analysis

## Overview

- **Project**: /tmp/redsl-autonomous/vallm
- **Primary Language**: python
- **Languages**: python: 94, shell: 9
- **Analysis Mode**: static
- **Total Functions**: 425
- **Total Classes**: 44
- **Modules**: 103
- **Entry Points**: 0

## Architecture by Module

### src.vallm.cli.batch_processor_impl
- **Functions**: 21
- **Classes**: 1
- **File**: `batch_processor_impl.py`

### src.vallm.cli.output_formatters.batch
- **Functions**: 16
- **File**: `batch.py`

### examples.11_claude_code_autonomous.legacy_code.data_processor
- **Functions**: 16
- **Classes**: 2
- **File**: `data_processor.py`

### src.vallm.validators.semantic
- **Functions**: 15
- **Classes**: 1
- **File**: `semantic.py`

### mcp.server._tools_vallm
- **Functions**: 14
- **File**: `_tools_vallm.py`

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

### src.vallm.validators.imports.python_imports
- **Functions**: 9
- **Classes**: 1
- **File**: `python_imports.py`

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

### src.vallm.core.ast_compare
- **Functions**: 8
- **File**: `ast_compare.py`

### src.vallm.validators.file_cache
- **Functions**: 7
- **Classes**: 1
- **File**: `file_cache.py`

## Key Entry Points

Main execution flows into the system:

## Process Flows

Key execution flows identified:

## Key Classes

### src.vallm.cli.batch_processor_impl.BatchProcessor
> Handles batch validation of multiple files.
- **Methods**: 21
- **Key Methods**: src.vallm.cli.batch_processor_impl.BatchProcessor.__init__, src.vallm.cli.batch_processor_impl.BatchProcessor.process_batch, src.vallm.cli.batch_processor_impl.BatchProcessor.output_batch_results, src.vallm.cli.batch_processor_impl.BatchProcessor._load_gitignore_parser, src.vallm.cli.batch_processor_impl.BatchProcessor._build_file_list, src.vallm.cli.batch_processor_impl.BatchProcessor._parse_filter_patterns, src.vallm.cli.batch_processor_impl.BatchProcessor._should_exclude_file, src.vallm.cli.batch_processor_impl.BatchProcessor._matches_include_pattern, src.vallm.cli.batch_processor_impl.BatchProcessor._filter_files, src.vallm.cli.batch_processor_impl.BatchProcessor._handle_no_files_found

### src.vallm.validators.semantic.SemanticValidator
> Tier 3: LLM-as-judge semantic code review.
- **Methods**: 15
- **Key Methods**: src.vallm.validators.semantic.SemanticValidator.__init__, src.vallm.validators.semantic.SemanticValidator.validate, src.vallm.validators.semantic.SemanticValidator._build_prompt, src.vallm.validators.semantic.SemanticValidator._call_llm, src.vallm.validators.semantic.SemanticValidator._call_ollama, src.vallm.validators.semantic.SemanticValidator._call_litellm, src.vallm.validators.semantic.SemanticValidator._call_http, src.vallm.validators.semantic.SemanticValidator._parse_response, src.vallm.validators.semantic.SemanticValidator._extract_json_from_response, src.vallm.validators.semantic.SemanticValidator._create_parse_error_result
- **Inherits**: BaseValidator

### src.vallm.validators.regression.RegressionValidator
> Tier 2: Run pytest against proposed code and report pass/fail.

The validator writes the proposed co
- **Methods**: 10
- **Key Methods**: src.vallm.validators.regression.RegressionValidator.__init__, src.vallm.validators.regression.RegressionValidator.validate, src.vallm.validators.regression.RegressionValidator._resolve_test_dir, src.vallm.validators.regression.RegressionValidator._write_code, src.vallm.validators.regression.RegressionValidator._build_pytest_cmd, src.vallm.validators.regression.RegressionValidator._run_pytest, src.vallm.validators.regression.RegressionValidator._interpret, src.vallm.validators.regression.RegressionValidator._parse_failures, src.vallm.validators.regression.RegressionValidator._timeout_result, src.vallm.validators.regression.RegressionValidator._exception_result
- **Inherits**: BaseValidator

### examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor
> Data processor with multiple responsibilities - violates SRP.
- **Methods**: 10
- **Key Methods**: examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.__init__, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.process_user_data, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.calculate_metrics, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.export_data, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.validate_email, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.validate_email_again, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.process_with_external_api, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.complex_calculation, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.unused_function, examples.11_claude_code_autonomous.legacy_code.data_processor.DataProcessor.another_unused_function

### src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator
> JavaScript/TypeScript import validator.
- **Methods**: 7
- **Key Methods**: src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.__init__, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.validate, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.extract_imports, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.module_exists, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.get_language, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator._get_error_message, src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator._get_rule_name
- **Inherits**: BaseImportValidator

### src.vallm.validators.imports.python_imports.PythonImportValidator
> Python-specific import validator.
- **Methods**: 7
- **Key Methods**: src.vallm.validators.imports.python_imports.PythonImportValidator.validate, src.vallm.validators.imports.python_imports.PythonImportValidator._relative_import_exists, src.vallm.validators.imports.python_imports.PythonImportValidator.extract_imports, src.vallm.validators.imports.python_imports.PythonImportValidator.module_exists, src.vallm.validators.imports.python_imports.PythonImportValidator.get_language, src.vallm.validators.imports.python_imports.PythonImportValidator._get_error_message, src.vallm.validators.imports.python_imports.PythonImportValidator._get_rule_name
- **Inherits**: BaseImportValidator

### src.vallm.validators.imports.base.BaseImportValidator
> Base class for all import validators.
- **Methods**: 7
- **Key Methods**: src.vallm.validators.imports.base.BaseImportValidator.validate, src.vallm.validators.imports.base.BaseImportValidator.extract_imports, src.vallm.validators.imports.base.BaseImportValidator.module_exists, src.vallm.validators.imports.base.BaseImportValidator.get_language, src.vallm.validators.imports.base.BaseImportValidator._get_error_message, src.vallm.validators.imports.base.BaseImportValidator._get_rule_name, src.vallm.validators.imports.base.BaseImportValidator.create_validation_result
- **Inherits**: ABC

### src.vallm.core.languages.Language
> Supported programming languages with their tree-sitter identifiers.
- **Methods**: 7
- **Key Methods**: src.vallm.core.languages.Language.__init__, src.vallm.core.languages.Language.from_extension, src.vallm.core.languages.Language.from_path, src.vallm.core.languages.Language.from_string, src.vallm.core.languages.Language.is_compiled, src.vallm.core.languages.Language.is_scripting, src.vallm.core.languages.Language.is_web
- **Inherits**: Enum

### examples.10_mcp_ollama_demo.refactored_output.OrderManager
> Class with single responsibility - adheres to SOLID principles.
- **Methods**: 7
- **Key Methods**: examples.10_mcp_ollama_demo.refactored_output.OrderManager.__init__, examples.10_mcp_ollama_demo.refactored_output.OrderManager.add_order, examples.10_mcp_ollama_demo.refactored_output.OrderManager.validate_order, examples.10_mcp_ollama_demo.refactored_output.OrderManager.execute_query, examples.10_mcp_ollama_demo.refactored_output.OrderManager.process_payment, examples.10_mcp_ollama_demo.refactored_output.OrderManager.send_email, examples.10_mcp_ollama_demo.refactored_output.OrderManager.get_stats

### src.vallm.validators.semantic_cache.SemanticCache
> Cache for semantic validation results to improve performance.
- **Methods**: 6
- **Key Methods**: src.vallm.validators.semantic_cache.SemanticCache.__init__, src.vallm.validators.semantic_cache.SemanticCache._get_cache_key, src.vallm.validators.semantic_cache.SemanticCache.get, src.vallm.validators.semantic_cache.SemanticCache.set, src.vallm.validators.semantic_cache.SemanticCache.clear, src.vallm.validators.semantic_cache.SemanticCache.get_cache_stats

### src.vallm.validators.file_cache.FileValidationCache
> In-memory cache keyed on file path + mtime + size.
- **Methods**: 6
- **Key Methods**: src.vallm.validators.file_cache.FileValidationCache.__init__, src.vallm.validators.file_cache.FileValidationCache._key, src.vallm.validators.file_cache.FileValidationCache.get, src.vallm.validators.file_cache.FileValidationCache.set, src.vallm.validators.file_cache.FileValidationCache.clear, src.vallm.validators.file_cache.FileValidationCache.stats

### src.vallm.core.gitignore.GitignoreParser
> Parse .gitignore files and match paths against patterns.
- **Methods**: 6
- **Key Methods**: src.vallm.core.gitignore.GitignoreParser.__init__, src.vallm.core.gitignore.GitignoreParser._parse, src.vallm.core.gitignore.GitignoreParser.matches, src.vallm.core.gitignore.GitignoreParser._match_pattern, src.vallm.core.gitignore.GitignoreParser._fnmatch, src.vallm.core.gitignore.GitignoreParser._pattern_to_regex

### examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager
> Class with mixed responsibilities - SOLID violation.
- **Methods**: 6
- **Key Methods**: examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.__init__, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.add_order, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.execute_query, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.process_payment, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.send_email, examples.10_mcp_ollama_demo.legacy_code.order_processor.OrderManager.get_stats

### src.vallm.validators.security.SecurityValidator
> Tier 2: Security analysis using built-in patterns and optionally bandit.
- **Methods**: 5
- **Key Methods**: src.vallm.validators.security.SecurityValidator.validate, src.vallm.validators.security.SecurityValidator._check_patterns, src.vallm.validators.security.SecurityValidator._check_python_ast, src.vallm.validators.security.SecurityValidator._get_func_name, src.vallm.validators.security.SecurityValidator._try_bandit
- **Inherits**: BaseValidator

### src.vallm.validators.lint.LintValidator
> Validator for linting issues using ruff.
- **Methods**: 5
- **Key Methods**: src.vallm.validators.lint.LintValidator.__init__, src.vallm.validators.lint.LintValidator.validate, src.vallm.validators.lint.LintValidator._check_ruff, src.vallm.validators.lint.LintValidator._parse_ruff_result, src.vallm.validators.lint.LintValidator._parse_ruff_text

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

### src.vallm.validators.imports.go_imports.GoImportValidator
> Go import validator.
- **Methods**: 5
- **Key Methods**: src.vallm.validators.imports.go_imports.GoImportValidator.get_language, src.vallm.validators.imports.go_imports.GoImportValidator._get_error_message, src.vallm.validators.imports.go_imports.GoImportValidator._get_rule_name, src.vallm.validators.imports.go_imports.GoImportValidator.extract_imports, src.vallm.validators.imports.go_imports.GoImportValidator.module_exists
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

## Data Transformation Functions

Key functions that process and transform data:

### src.vallm.hookspecs.VallmSpec.validate_proposal
> Validate a code proposal and return a ValidationResult.

### src.vallm.validators.syntax.SyntaxValidator.validate
- **Output to**: ValidationResult, self._validate_python, self._validate_treesitter

### src.vallm.validators.syntax.SyntaxValidator._validate_python
> Validate Python syntax using ast.parse and tree-sitter.
- **Output to**: ast.parse, src.vallm.core.ast_compare.tree_sitter_error_count, issues.append, issues.append, Issue

### src.vallm.validators.syntax.SyntaxValidator._validate_treesitter
> Validate non-Python syntax using tree-sitter.
- **Output to**: src.vallm.core.ast_compare.tree_sitter_error_count, issues.append, issues.append, Issue, Issue

### src.vallm.validators.security.SecurityValidator.validate
- **Output to**: self._check_patterns, issues.extend, _LANGUAGE_PATTERNS.get, ValidationResult, self._check_patterns

### src.vallm.validators.semantic.SemanticValidator.validate
- **Output to**: self.cache.get, self._build_prompt, self._call_llm, self._parse_response, self.cache.set

### src.vallm.validators.semantic.SemanticValidator._parse_response
> Parse LLM JSON response into a ValidationResult.
- **Output to**: self._extract_json_from_response, self._parse_scores, self._parse_issues, ValidationResult, isinstance

### src.vallm.validators.semantic.SemanticValidator._create_parse_error_result
> Create result for when JSON cannot be parsed from response.
- **Output to**: ValidationResult, Issue

### src.vallm.validators.semantic.SemanticValidator._parse_scores
> Parse and normalize scores from LLM response.
- **Output to**: data.get, isinstance, max, min

### src.vallm.validators.semantic.SemanticValidator._parse_issues
> Parse issues from LLM response.
- **Output to**: data.get, self._parse_severity, self._parse_line_number, issues.append, isinstance

### src.vallm.validators.semantic.SemanticValidator._parse_severity
> Parse severity string into Severity enum.
- **Output to**: severity_map.get, severity_str.lower

### src.vallm.validators.semantic.SemanticValidator._parse_line_number
> Parse line number from various formats.
- **Output to**: isinstance, isinstance, int

### src.vallm.validators.regression.RegressionValidator.validate
- **Output to**: self._resolve_test_dir, tempfile.TemporaryDirectory, self._write_code, self._run_pytest, Path

### src.vallm.validators.regression.RegressionValidator._parse_failures
> Extract individual FAILED lines from pytest -q output.
- **Output to**: stdout.splitlines, line.strip, stripped.startswith, None.strip, issues.append

### src.vallm.validators.logical.LogicalErrorValidator.validate
> Validate code for logical errors using pyflakes.

Args:
    proposal: Code proposal to validate
    
- **Output to**: self._check_pyflakes, ValidationResult, ValidationResult, len, len

### src.vallm.validators.logical.LogicalErrorValidator._parse_pyflakes_line
> Parse a pyflakes output line into an Issue.

Args:
    line: Pyflakes output line
    
Returns:
    
- **Output to**: line.split, int, any, Issue, len

### src.vallm.validators.lint.LintValidator.validate
> Validate code for linting issues using ruff.

Args:
    proposal: Code proposal to validate
    cont
- **Output to**: self._check_ruff, ValidationResult, ValidationResult, len, len

### src.vallm.validators.lint.LintValidator._parse_ruff_result
> Parse a ruff JSON result into an Issue.

Args:
    item: Ruff result dictionary
    
Returns:
    Is
- **Output to**: any, Issue, None.startswith, None.startswith, item.get

### src.vallm.validators.lint.LintValidator._parse_ruff_text
> Parse ruff text output as fallback.

Args:
    output: Ruff text output
    
Returns:
    List of Is
- **Output to**: None.split, line.strip, output.strip, line.split, len

### src.vallm.validators.base.BaseValidator.validate
> Validate a proposal and return a result.

### src.vallm.validators.imports.wrapper.ImportValidator.validate
> Validate imports by dispatching to language-specific validators.
- **Output to**: ImportValidatorFactory.create_validator, validator.validate, ValidationResult

### src.vallm.validators.complexity.ComplexityValidator.validate
- **Output to**: self._check_lizard, issues.extend, details.update, min, ValidationResult

### src.vallm.validators.imports.utils.validate_import_path
> Validate if an import path is resolvable.

Args:
    import_path: The import path to validate
    so
- **Output to**: import_path.startswith, local_module.exists, local_pkg.exists, import_path.split, len

### src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.validate
> Validate JavaScript/TypeScript imports using tree-sitter.
- **Output to**: self.extract_imports, self.create_validation_result, len, self.module_exists, issues.append

### src.vallm.validators.imports.python_imports.PythonImportValidator.validate
> Validate Python imports using AST.
- **Output to**: ast.parse, self.extract_imports, self.create_validation_result, import_info.get, len

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `examples.11_claude_code_autonomous.claude_autonomous_demo.analyze_with_code2llm` - 43 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.run_autonomous_workflow` - 42 calls
- `examples.utils.validation_runner.run_validation_examples` - 40 calls
- `examples.utils.run_validation_examples` - 40 calls
- `examples.04_graph_analysis.main.main` - 40 calls
- `examples.10_mcp_ollama_demo.mcp_demo.analyze_with_code2llm` - 36 calls
- `examples.10_mcp_ollama_demo.mcp_demo.run_mcp_workflow` - 36 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.main` - 34 calls
- `examples.12_ollama_simple_demo.ollama_simple_demo.run_simple_workflow` - 31 calls
- `examples.02_ast_comparison.main.main` - 31 calls
- `src.vallm.cli.command_handlers.batch_command` - 30 calls
- `src.vallm.cli.output_formatters.output_batch_yaml` - 29 calls
- `src.vallm.cli.output_formatters.batch.output_batch_yaml` - 29 calls
- `examples.12_ollama_simple_demo.ollama_simple_demo.analyze_with_code2llm` - 29 calls
- `examples.12_ollama_simple_demo.ollama_simple_demo.main` - 29 calls
- `examples.05_llm_semantic_review.main.main` - 29 calls
- `examples.03_security_check.main.main` - 29 calls
- `examples.10_mcp_ollama_demo.mcp_demo.main` - 27 calls
- `src.vallm.cli.output_formatters.output_batch_toon` - 22 calls
- `src.vallm.cli.output_formatters.batch.output_batch_toon` - 22 calls
- `src.vallm.cli.command_handlers.validate_command` - 21 calls
- `examples.08_code2llm_integration.main.generate_report` - 20 calls
- `src.vallm.validators.imports.javascript_imports.JavaScriptImportValidator.extract_imports` - 19 calls
- `src.vallm.validators.imports.go_imports.GoImportValidator.extract_imports` - 18 calls
- `scripts.bump_version.main` - 18 calls
- `examples.09_code2logic_integration.main.main` - 18 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.create_basic_tests` - 17 calls
- `examples.09_code2logic_integration.main.analyze_with_code2logic` - 17 calls
- `examples.09_code2logic_integration.main.generate_report` - 17 calls
- `examples.07_multi_language.main.main` - 17 calls
- `src.vallm.validators.imports.rust_imports.RustImportValidator.extract_imports` - 16 calls
- `src.vallm.validators.imports.python_imports.PythonImportValidator.validate` - 16 calls
- `src.vallm.cli.output_formatters.output_batch_text` - 16 calls
- `src.vallm.cli.output_formatters.build_results_table` - 16 calls
- `src.vallm.cli.output_formatters.batch.output_batch_text` - 16 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.run_runtime_tests` - 16 calls
- `examples.08_code2llm_integration.main.validate_with_vallm` - 16 calls
- `src.vallm.cli.output_formatters.output_batch_empty` - 15 calls
- `src.vallm.cli.output_formatters.batch.output_batch_empty` - 15 calls
- `examples.11_claude_code_autonomous.claude_autonomous_demo.call_claude_code` - 15 calls

## System Interactions

How components interact:

```mermaid
graph TD
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.