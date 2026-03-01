#!/bin/bash
set -e

# Check if local Ollama is available
echo "🔗 Checking for local Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Local Ollama not found at http://localhost:11434"
    echo "Please start Ollama locally first:"
    echo "  ollama serve"
    exit 1
fi

echo "✓ Local Ollama is accessible!"

# Check if Qwen 2.5 Coder 7B model is available
echo "📦 Checking for qwen2.5-coder:7b model..."
if ! curl -s http://localhost:11434/api/tags | grep -q "qwen2.5-coder:7b"; then
    echo "❌ qwen2.5-coder:7b model not found locally"
    echo "Please pull the model first:"
    echo "  ollama pull qwen2.5-coder:7b"
    exit 1
else
    echo "✓ Model available locally"
fi

# Execute the provided command or default to bash
if [ $# -eq 0 ]; then
    echo ""
    echo "🎯 Ready to use local Ollama with qwen2.5-coder:7b!"
    echo "   API available at: http://localhost:11434"
    echo ""
    exec bash
else
    exec "$@"
fi
