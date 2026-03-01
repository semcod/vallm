#!/bin/bash
set -e

# Check if local Ollama is available
echo "🔗 Checking for local Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Local Ollama is accessible!"
    
    # Check if model is available
    if curl -s http://localhost:11434/api/tags | grep -q "qwen2.5-coder"; then
        echo "✓ qwen2.5-coder model is available"
    else
        echo "⚠ qwen2.5-coder model not found"
        echo "  Pull it with: ollama pull qwen2.5-coder:7b"
    fi
else
    echo "❌ Local Ollama not found"
    echo "Please start Ollama first:"
    echo "  ollama serve"
    exit 1
fi

# Execute the provided command or default to bash
if [ $# -eq 0 ]; then
    echo ""
    echo "🎯 Ready to run Simple Ollama demo!"
    echo ""
    exec bash
else
    exec "$@"
fi
