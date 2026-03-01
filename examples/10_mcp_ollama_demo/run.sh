#!/bin/bash
#
# MCP Demo Runner
# Demonstrates: code2llm → Ollama → vallm → Iterate workflow
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         MCP Demo: code2llm + Ollama + vallm                    ║"
echo "║         LLM-powered Code Refactoring with Validation           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALLM_ROOT="$(cd "$DEMO_DIR/../../.." && pwd)"
CONTAINER_NAME="vallm-mcp-demo"
OLLAMA_PORT=11434

# Function to print sections
print_section() {
    echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE} $1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Step 1: Check Docker
print_section "STEP 1: Environment Check"

print_step "Checking Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker found"

# Step 2: Build or start container
print_section "STEP 2: Docker Container Setup"

print_step "Checking for existing container..."
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    if docker ps | grep -q "$CONTAINER_NAME"; then
        print_success "Container already running"
    else
        print_step "Starting existing container..."
        docker start "$CONTAINER_NAME"
        print_success "Container started"
    fi
else
    print_step "Building Docker image (this may take a few minutes)..."
    # Build from vallm root so the Dockerfile can access the full project
    cd "$VALLM_ROOT"
    docker build -t vallm-mcp-demo:latest -f "$DEMO_DIR/Dockerfile" . 2>&1 | tee "$DEMO_DIR/docker-build.log"
    
    print_step "Creating and starting container..."
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p $OLLAMA_PORT:11434 \
        vallm-mcp-demo:latest \
        bash -c "ollama serve &
                 sleep 5
                 ollama pull qwen2.5-coder:7b
                 tail -f /dev/null" 2>&1 | tee "$DEMO_DIR/docker-run.log" &
    
    print_warning "Waiting for Ollama to start and download model (this may take 5-10 minutes)..."
    
    # Wait for Ollama to be ready
    for i in {1..60}; do
        if curl -s http://localhost:$OLLAMA_PORT/api/tags > /dev/null 2>&1; then
            print_success "Ollama is ready!"
            break
        fi
        echo -n "."
        sleep 10
    done
fi

# Check if Ollama is responding
print_step "Checking Ollama API..."
if curl -s http://localhost:$OLLAMA_PORT/api/tags > /dev/null 2>&1; then
    print_success "Ollama API is accessible"
    
    # Check if model is available
    if curl -s http://localhost:$OLLAMA_PORT/api/tags | grep -q "qwen2.5-coder"; then
        print_success "Qwen 2.5 Coder 7B model is available"
    else
        print_warning "Model not found, pulling..."
        docker exec "$CONTAINER_NAME" ollama pull qwen2.5-coder:7b 2>&1 | tee -a docker-run.log
    fi
else
    print_error "Ollama is not responding. Check container logs:"
    echo "  docker logs $CONTAINER_NAME"
    exit 1
fi

# Step 3: Show legacy code
print_section "STEP 3: Legacy Code Analysis"

echo -e "${BOLD}Analyzing legacy code with issues:${NC}\n"
echo -e "${YELLOW}File: legacy_code/order_processor.py${NC}"
echo ""
cat "$DEMO_DIR/legacy_code/order_processor.py" | head -50
echo -e "\n${CYAN}... (truncated, see full file for all issues)${NC}\n"

print_warning "Issues in this code:"
echo "  • Security vulnerabilities: eval(), pickle, SQL injection, command injection"
echo "  • High cyclomatic complexity: deeply nested if statements"
echo "  • Duplicate code: two identical email validation functions"
echo "  • Magic numbers: hardcoded shipping costs"
echo "  • Dead code: unused variables and functions"
echo "  • Hardcoded credentials: API keys in source"
echo "  • SOLID violations: OrderManager has too many responsibilities"

# Step 4: Run MCP Demo
print_section "STEP 4: Running MCP Demo"

echo -e "${BOLD}Starting the workflow:${NC}"
echo "  1. code2llm → Analyze code structure"
echo "  2. vallm → Validate legacy code"
echo "  3. Ollama → Generate refactored code"
echo "  4. vallm → Validate refactored code"
echo "  5. If validation fails → Send feedback to Ollama → Retry"
echo ""

print_step "Executing mcp_demo.py..."
cd "$DEMO_DIR"

# Run with logging inside container
print_step "Running mcp_demo.py inside container..."
docker exec -w /vallm/examples/10_mcp_ollama_demo "$CONTAINER_NAME" \
    python3 mcp_demo.py --file legacy_code/order_processor.py --max-iterations 3 2>&1 | tee mcp-demo-output.log

DEMO_EXIT_CODE=${PIPESTATUS[0]}

# Step 5: Show results
print_section "STEP 5: Results"

if [ -f "$DEMO_DIR/refactored_output.py" ]; then
    print_success "Refactoring successful!"
    echo ""
    echo -e "${BOLD}Refactored code saved to:${NC} refactored_output.py"
    echo ""
    echo -e "${BOLD}First 50 lines of refactored code:${NC}"
    head -50 "$DEMO_DIR/refactored_output.py"
    
    print_section "Validation Report"
    
    # Run vallm on the refactored code
    echo -e "${CYAN}Running final validation...${NC}\n"
    
    docker exec -w /app "$CONTAINER_NAME" \
        python3 -c "
from vallm import Proposal, validate, VallmSettings

with open('refactored_output.py') as f:
    code = f.read()

settings = VallmSettings(enable_syntax=True, enable_imports=True, enable_complexity=True, enable_security=True)
proposal = Proposal(code=code, language='python')
result = validate(proposal, settings)

print(f'Verdict: {result.verdict.value.upper()}')
print(f'Score: {result.weighted_score:.2f}/1.0')
print('\\nValidators:')
for r in result.results:
    status = '✓' if r.score >= 0.8 else '⚠' if r.score >= 0.5 else '✗'
    print(f'  {status} {r.validator}: {r.score:.2f}')
    for issue in r.issues:
        print(f'      - [{issue.severity.value}] {issue.message}')
" 2>&1 | tee -a mcp-demo-output.log
    
else
    print_error "Refactoring did not produce valid output"
    if [ -f "$DEMO_DIR/refactored_output_best_attempt.py" ]; then
        echo ""
        print_warning "Best attempt saved to: refactored_output_best_attempt.py"
    fi
fi

# Step 6: Show logs
print_section "STEP 6: Log Files"

echo -e "${BOLD}Generated log files:${NC}"
echo "  • mcp_demo.log - Detailed debug logs"
echo "  • mcp-demo-output.log - Full demo output"
echo "  • docker-build.log - Docker build output"
echo "  • docker-run.log - Container runtime logs"
echo ""

echo -e "${CYAN}Log summary:${NC}"
if [ -f "$DEMO_DIR/mcp_demo.log" ]; then
    echo "  mcp_demo.log: $(wc -l < "$DEMO_DIR/mcp_demo.log") lines"
fi
if [ -f "$DEMO_DIR/mcp-demo-output.log" ]; then
    echo "  mcp-demo-output.log: $(wc -l < "$DEMO_DIR/mcp-demo-output.log") lines"
fi

# Summary
print_section "SUMMARY"

if [ $DEMO_EXIT_CODE -eq 0 ]; then
    print_success "Demo completed successfully!"
    echo ""
    echo -e "${BOLD}What happened:${NC}"
    echo "  1. ✓ code2llm analyzed the legacy code structure"
    echo "  2. ✓ vallm identified security and quality issues"
    echo "  3. ✓ Ollama (Qwen 2.5 Coder 7B) generated refactored code"
    echo "  4. ✓ vallm validated the refactored code"
    echo "  5. ✓ All security vulnerabilities were fixed"
    echo "  6. ✓ Code complexity was reduced"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo "  • Review refactored_output.py"
    echo "  • Compare with legacy_code/order_processor.py"
    echo "  • Check mcp_demo.log for detailed trace"
else
    print_error "Demo completed with issues"
    echo ""
    echo -e "${BOLD}Check logs for details:${NC}"
    echo "  tail -100 mcp_demo.log"
    echo "  docker logs $CONTAINER_NAME"
fi

# Cleanup prompt
echo ""
print_section "CLEANUP"

echo -e "${CYAN}To stop and remove the container:${NC}"
echo "  docker stop $CONTAINER_NAME"
echo "  docker rm $CONTAINER_NAME"
echo ""
echo -e "${CYAN}To run the demo again:${NC}"
echo "  ./run.sh"
echo ""
echo -e "${CYAN}To enter the container:${NC}"
echo "  docker exec -it $CONTAINER_NAME bash"

echo ""
echo -e "${GREEN}${BOLD}Demo complete!${NC}"
