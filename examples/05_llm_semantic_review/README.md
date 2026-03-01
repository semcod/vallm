# LLM Semantic Review Example

## Overview
This example demonstrates vallm's LLM-as-judge semantic review capabilities using a local Ollama model for intelligent code analysis.

## Prerequisites
1. **Install Ollama**: https://ollama.com
2. **Pull the model**: `ollama pull qwen2.5-coder:7b`
3. **Install ollama package**: `pip install ollama`
4. **Start Ollama service**: `ollama serve`

## What it Tests
- **LLM-powered semantic analysis**: Using AI for deep code understanding
- **Bug detection**: Identifying subtle logic errors (off-by-one, etc.)
- **Code quality assessment**: Evaluating coding practices and style
- **Reference-based comparison**: Comparing against correct implementations

## Code Samples
The example analyzes three different code scenarios:
1. **Buggy binary search** - Contains off-by-one error in loop bounds
2. **Correct binary search** - Reference implementation for comparison
3. **Poor practices code** - Functionally correct but with bad style

## Running the Example
```bash
cd 05_llm_semantic_review
python main.py
```

## Expected Output
- LLM semantic scores and detailed assessments
- Bug detection with specific issue descriptions
- Code quality evaluations with improvement suggestions
- Comparison scores when reference code is provided

## Configuration
The example uses:
- **Provider**: Ollama (local LLM)
- **Model**: qwen2.5-coder:7b (coding-focused model)
- **Base URL**: http://localhost:11434 (default Ollama endpoint)

## Analysis Data
After running, analysis results will be saved in the `.vallm/` folder within this directory, including:
- LLM review reports and scores
- Detailed semantic analysis
- Bug detection results
- Code quality assessments
