#!/usr/bin/env bash
pip install code2logic --upgrade
pip install code2llm --upgrade

#code2logic ./ -f toon --compact --no-repeat-module --function-logic --with-schema --name project -o ./

code2logic ./ -f toon --compact --name project -o ./
code2llm ./ -f toon,evolution -o ./project
# Run vallm batch validation on the project
vallm batch ./src ./examples --recursive --include "*.py" 2>/dev/null || echo "vallm validation skipped (not installed)"
#vallm batch ./examples --recursive