#!/bin/bash
#
# Simple Ollama Demo Runner
# Demonstrates: code2llm → Ollama → vallm → Test
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Simple Ollama Demo: code2llm → Ollama → vallm          ║"
echo "║         Basic Autonomous Refactoring with Local LLM            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALLM_ROOT="$(cd "$DEMO_DIR/../.." && pwd)"
CONTAINER_NAME="ollama-simple-demo"

echo -e "${BOLD}${CYAN}Simple Ollama Demo - Local LLM Refactoring${NC}"
echo -e "${CYAN}This demo uses your local Ollama instance for code refactoring${NC}\n"

# Step 1: Check Ollama
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE} STEP 1: Environment Check${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${CYAN}▶ Checking Ollama...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
    
    # Check if model is available
    if curl -s http://localhost:11434/api/tags | grep -q "qwen2.5-coder"; then
        echo -e "${GREEN}✓ qwen2.5-coder model is available${NC}"
    else
        echo -e "${YELLOW}⚠ qwen2.5-coder model not found${NC}"
        echo -e "${YELLOW}  Pull it with: ollama pull qwen2.5-coder:7b${NC}"
    fi
else
    echo -e "${RED}✗ Ollama is not running${NC}"
    echo -e "${YELLOW}  Start it with: ollama serve${NC}"
    exit 1
fi

# Step 2: Docker Setup
echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE} STEP 2: Docker Container Setup${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${CYAN}▶ Checking for existing container...${NC}"
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo -e "${CYAN}▶ Removing existing container...${NC}"
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
fi

echo -e "${CYAN}▶ Building Docker image...${NC}"
cd "$VALLM_ROOT"
docker build --no-cache -t ollama-simple-demo:latest -f "$DEMO_DIR/Dockerfile" . 2>&1 | tee "$DEMO_DIR/docker-build.log"

echo -e "${CYAN}▶ Creating and starting container...${NC}"
docker run -d \
    --name "$CONTAINER_NAME" \
    --network host \
    ollama-simple-demo:latest \
    tail -f /dev/null 2>&1 | tee "$DEMO_DIR/docker-run.log" &

echo -e "${YELLOW}⚠ Waiting for container to start...${NC}"
sleep 3

# Step 3: Show Legacy Code
echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE} STEP 3: Legacy Code Analysis${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${BOLD}Analyzing buggy code:${NC}\n"
echo -e "${YELLOW}File: legacy_code/simple_buggy.py${NC}"
echo ""
cat "$DEMO_DIR/legacy_code/simple_buggy.py" | head -40

echo -e "\n${YELLOW}⚠ Issues in this code:${NC}"
echo "  • Security vulnerabilities: eval(), os.system(), SQL injection"
echo "  • No error handling on file operations"
echo "  • Duplicate function names"
echo "  • Unused variables and functions"
echo "  • Deep nesting in methods"
echo "  • Global variables"

# Step 4: Run Demo
echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE} STEP 4: Running Simple Ollama Demo${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${BOLD}Starting workflow:${NC}"
echo "  1. code2llm → Analyze code structure"
echo "  2. Ollama → Generate refactored code"
echo "  3. vallm → Validate code quality"
echo "  4. Syntax test → Basic validation"
echo "  5. Loop until perfect (max 3 iterations)"

echo -e "\n${CYAN}▶ Executing ollama_simple_demo.py...${NC}"
cd "$DEMO_DIR"

echo -e "${CYAN}▶ Running demo inside container...${NC}"
docker exec -w /vallm/examples/12_ollama_simple_demo "$CONTAINER_NAME" \
    python3 ollama_simple_demo.py --file legacy_code/simple_buggy.py --max-iterations 3 2>&1 | tee ollama-simple-output.log

DEMO_EXIT_CODE=${PIPESTATUS[0]}

echo -e "${CYAN}▶ Copying results from container...${NC}"
docker cp "$CONTAINER_NAME:/vallm/examples/12_ollama_simple_demo/best_version.py" "$DEMO_DIR/" 2>/dev/null || true
docker cp "$CONTAINER_NAME:/vallm/examples/12_ollama_simple_demo/ollama_simple.log" "$DEMO_DIR/" 2>/dev/null || true

# Copy iteration files
for i in {1..3}; do
    docker cp "$CONTAINER_NAME:/vallm/examples/12_ollama_simple_demo/iteration_${i}.py" "$DEMO_DIR/" 2>/dev/null || true
done

# Step 5: Show Results
echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE} STEP 5: Results${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ -f "$DEMO_DIR/best_version.py" ]; then
    echo -e "${GREEN}✓ Refactoring completed!${NC}"
    
    echo -e "\n${BOLD}Best refactored version:${NC}"
    echo "  File: best_version.py"
    echo "  Size: $(wc -l < "$DEMO_DIR/best_version.py") lines"
    
    echo -e "\n${BOLD}Improvement summary:${NC}"
    echo "  Original: $(wc -l < "$DEMO_DIR/legacy_code/simple_buggy.py") lines"
    echo "  Refactored: $(wc -l < "$DEMO_DIR/best_version.py") lines"
    
    echo -e "\n${BOLD}Sample of refactored code:${NC}"
    head -20 "$DEMO_DIR/best_version.py" | cat -n
else
    echo -e "${YELLOW}⚠ Refactoring completed with limitations${NC}"
fi

# Step 6: Summary
echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE} SUMMARY${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${BOLD}Generated files:${NC}"
echo "  • best_version.py - Final refactored code"
echo "  • iteration_*.py - All iteration versions"
echo "  • ollama_simple.log - Detailed logs"
echo "  • ollama-simple-output.log - Console output"

echo -e "\n${CYAN}Log summary:${NC}"
if [ -f "$DEMO_DIR/ollama_simple.log" ]; then
    echo "  ollama_simple.log: $(wc -l < "$DEMO_DIR/ollama_simple.log") lines"
fi

if [ -f "$DEMO_DIR/best_version.py" ]; then
    echo -e "\n${GREEN}🎉 Simple Ollama demo completed successfully!${NC}"
    echo ""
    echo -e "${BOLD}Achievements:${NC}"
    echo "  • Used local Ollama for code refactoring"
    echo "  • Autonomous improvement loop"
    echo "  • Multi-criteria validation"
    echo "  • Best version tracking"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo "  • Review best_version.py"
    echo "  • Compare with original code"
    echo "  • Check ollama_simple.log"
else
    echo -e "\n${YELLOW}⚠ Demo completed with issues${NC}"
    echo ""
    echo -e "${BOLD}Check logs:${NC}"
    echo "  tail -20 ollama_simple.log"
    echo "  docker logs $CONTAINER_NAME"
fi

# Cleanup
echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE} CLEANUP${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${CYAN}To stop and remove the container:${NC}"
echo "  docker stop $CONTAINER_NAME"
echo "  docker rm $CONTAINER_NAME"

echo -e "\n${CYAN}To run the demo again:${NC}"
echo "  ./run.sh"

echo -e "\n${CYAN}To enter the container:${NC}"
echo "  docker exec -it $CONTAINER_NAME bash"

echo -e "\n${GREEN}Simple Ollama demo complete!${NC}"
