# Vallm Examples

This directory contains comprehensive examples demonstrating vallm's code validation and analysis capabilities.

## 📁 Example Structure

Each example is organized in its own folder with:
- `main.py` - The main example script
- `README.md` - Detailed explanation of what the example demonstrates
- `.vallm/` - Generated analysis data (created after running)

## 🚀 Quick Start

### Run All Examples
```bash
# Run all examples sequentially
./run.sh
```

### Run Individual Examples
```bash
cd 01_basic_validation
python main.py
```

## 📋 Examples Overview

### 1. Basic Validation (`01_basic_validation/`)
**Demonstrates**: Core validation pipeline (syntax, imports, complexity)
- **Good code**: Clean Fibonacci implementation
- **Bad code**: Syntax error example  
- **Complex code**: Deeply nested conditionals

### 2. AST Comparison (`02_ast_comparison/`)
**Demonstrates**: Abstract Syntax Tree analysis and similarity scoring
- **Python AST similarity**: Comparing function implementations
- **Multi-language parsing**: JavaScript and C code analysis
- **Structural diffing**: Code change detection

### 3. Security Check (`03_security_check/`)
**Demonstrates**: Security vulnerability detection
- **Insecure patterns**: eval(), exec(), os.system, pickle.loads
- **Safe alternatives**: Secure coding practices
- **Risk assessment**: Security scoring and issue reporting

### 4. Graph Analysis (`04_graph_analysis/`)
**Demonstrates**: Code graph building and structural analysis
- **Import graphs**: Module dependency tracking
- **Call graphs**: Function relationship mapping
- **Change detection**: Breaking change identification

### 5. LLM Semantic Review (`05_llm_semantic_review/`)
**Demonstrates**: AI-powered semantic code analysis
- **Prerequisites**: Ollama with qwen2.5-coder:7b model
- **Bug detection**: Subtle logic error identification
- **Code quality**: Style and practice evaluation

### 6. Multi-language Validation (`06_multilang_validation/`)
**Demonstrates**: Cross-language validation capabilities
- **JavaScript**: ES6+ syntax and complexity
- **C**: C99/C11 standard compliance
- **Universal interface**: Consistent API across languages

## 📊 Analysis Data

Each example generates analysis data in its `.vallm/` folder:
- **JSON reports**: Structured validation results
- **Score breakdowns**: Detailed metric analysis
- **Issue details**: Specific problems found
- **Comparison data**: Before/after analysis

## 🛠️ Configuration

### Basic Examples
Examples 1-4 work out-of-the-box with vallm's default configuration.

### LLM Example (Example 5)
Requires additional setup:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull qwen2.5-coder:7b

# Start Ollama service
ollama serve

# Install Python package
pip install ollama
```

### Multi-language Example (Example 6)
Supports JavaScript and C out-of-the-box using tree-sitter parsers.

## 📈 Expected Output

Each example provides:
- **Real-time validation**: Live output during execution
- **Summary reports**: End-of-run analysis summary
- **Data persistence**: Results saved to `.vallm/` folder
- **Error handling**: Graceful failure reporting

## 🔧 Troubleshooting

### Common Issues
1. **Import errors**: Ensure vallm is properly installed
2. **LLM connection**: Check Ollama service is running for example 5
3. **Permission errors**: Ensure write access for `.vallm/` folder creation

### Debug Mode
Run individual examples to isolate issues:
```bash
cd 01_basic_validation
python main.py
```

## 📚 Further Reading

- [Main vallm documentation](../README.md)
- [API reference](../src/vallm/)
- [Configuration options](../src/vallm/config.py)

## 🤝 Contributing

To add new examples:
1. Create a new folder with numbered prefix
2. Add `main.py` with example code
3. Create `README.md` with documentation
4. Include analysis data generation
5. Update this overview and `run.sh` if needed
