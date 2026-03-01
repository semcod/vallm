#!/bin/bash
set -e

# Start Ollama in background
echo "🚀 Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is ready!"
        break
    fi
    sleep 1
done

# Pull Qwen 2.5 Coder 7B if not present
echo "📦 Checking for qwen2.5-coder:7b model..."
if ! ollama list | grep -q "qwen2.5-coder:7b"; then
    echo "⬇️  Pulling qwen2.5-coder:7b (this may take a while)..."
    ollama pull qwen2.5-coder:7b
    echo "✓ Model downloaded!"
else
    echo "✓ Model already present"
fi

# Execute the provided command or default to bash
if [ $# -eq 0 ]; then
    echo ""
    echo "🎯 Ollama is ready with qwen2.5-coder:7b!"
    echo "   API available at: http://localhost:11434"
    echo ""
    exec bash
else
    exec "$@"
fi
