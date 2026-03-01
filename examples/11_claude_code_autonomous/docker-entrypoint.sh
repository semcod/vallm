#!/bin/bash
set -e

# Check if local Ollama is available (for comparison)
echo "🔗 Checking for local Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Local Ollama is accessible!"
else
    echo "⚠ Local Ollama not found (not required for Claude demo)"
fi

# Check if ANTHROPIC_API_KEY is available
echo "🔑 Checking for ANTHROPIC_API_KEY..."
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✓ ANTHROPIC_API_KEY is set"
else
    echo "❌ ANTHROPIC_API_KEY not found"
    echo "Please set it with: export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

# Execute the provided command or default to bash
if [ $# -eq 0 ]; then
    echo ""
    echo "🎯 Ready to run Claude Code autonomous demo!"
    echo ""
    exec bash
else
    exec "$@"
fi
