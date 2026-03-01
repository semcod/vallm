#!/bin/bash
#
# Claude Code Autonomous Demo Runner
# Demonstrates: code2llm → Claude Code → vallm → Runtime Tests → code2llm (loop)
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${MAGENTA}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Claude Code Autonomous Demo: Full Refactoring Loop        ║"
echo "║     code2llm → Claude Code → vallm → Tests → code2llm        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALLM_ROOT="$(cd "$DEMO_DIR/../.." && pwd)"
CONTAINER_NAME="claude-autonomous-demo"

# Function to print sections
print_section() {
    echo -e "\n${BOLD}${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${MAGENTA} $1${NC}"
    echo -e "${BOLD}${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
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

# Step 1: Check environment
print_section "STEP 1: Environment Check"

print_step "Checking Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker found"

print_step "Checking ANTHROPIC_API_KEY..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    print_error "ANTHROPIC_API_KEY environment variable not set"
    echo "  Set it with: export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi
print_success "ANTHROPIC_API_KEY is set"

# Step 2: Docker Container Setup
print_section "STEP 2: Docker Container Setup"

print_step "Checking for existing container..."
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    if docker ps | grep -q "$CONTAINER_NAME"; then
        print_success "Container already running"
    else
        print_step "Removing existing container..."
        docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
    fi
fi

print_step "Building Docker image (this may take a few minutes)..."
# Build from vallm root so the Dockerfile can access the full project
cd "$VALLM_ROOT"
docker build --no-cache -t claude-autonomous-demo:latest -f "$DEMO_DIR/Dockerfile" . 2>&1 | tee "$DEMO_DIR/docker-build.log"

print_step "Creating and starting container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --network host \
    -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    claude-autonomous-demo:latest \
    tail -f /dev/null 2>&1 | tee "$DEMO_DIR/docker-run.log" &

print_warning "Waiting for container to start..."
sleep 5

# Check if container is running
if docker ps | grep -q "$CONTAINER_NAME"; then
    print_success "Container is running"
else
    print_error "Container failed to start"
    echo "Check logs: docker logs $CONTAINER_NAME"
    exit 1
fi

# Step 3: Show legacy code
print_section "STEP 3: Legacy Code Analysis"

echo -e "${BOLD}Analyzing legacy code with multiple issues:${NC}\n"
echo -e "${YELLOW}File: legacy_code/data_processor.py${NC}"
echo ""
cat "$DEMO_DIR/legacy_code/data_processor.py" | head -50

echo -e "\n${YELLOW}⚠ Issues in this code:${NC}"
echo "  • Security vulnerabilities: eval(), SQL injection, command injection, pickle"
echo "  • SOLID violations: DataProcessor has too many responsibilities"
echo "  • Performance issues: nested loops, inefficient calculations"
echo "  • Code smells: global variables, duplicate functions, dead code"
echo "  • Hardcoded credentials: API keys in source code"
echo "  • Tight coupling: ReportGenerator directly accesses DataProcessor internals"

# Step 4: Run Claude Code Autonomous Demo
print_section "STEP 4: Running Claude Code Autonomous Demo"

echo -e "${BOLD}Starting autonomous refactoring workflow:${NC}"
echo "  1. code2llm → Analyze code structure and smells"
echo "  2. Claude Code → Generate refactored solution"
echo "  3. vallm → Validate code quality and security"
echo "  4. Runtime Tests → Validate functionality"
echo "  5. code2llm → Re-analyze improvements"
echo "  6. Loop until perfect (max 5 iterations)"

print_step "Executing claude_autonomous_demo.py..."
cd "$DEMO_DIR"

# Run with logging inside container
print_step "Running demo inside container..."
docker exec -w /vallm/examples/11_claude_code_autonomous "$CONTAINER_NAME" \
    python3 claude_autonomous_demo.py --file legacy_code/data_processor.py --max-iterations 5 2>&1 | tee claude-autonomous-output.log

DEMO_EXIT_CODE=${PIPESTATUS[0]}

print_step "Copying results from container..."
docker cp "$CONTAINER_NAME:/vallm/examples/11_claude_code_autonomous/best_refactored.py" "$DEMO_DIR/" 2>/dev/null || true
docker cp "$CONTAINER_NAME:/vallm/examples/11_claude_code_autonomous/claude_autonomous.log" "$DEMO_DIR/" 2>/dev/null || true

# Copy all iteration files
for i in {1..5}; do
    docker cp "$CONTAINER_NAME:/vallm/examples/11_claude_code_autonomous/refactored_v${i}.py" "$DEMO_DIR/" 2>/dev/null || true
done

# Step 5: Show results
print_section "STEP 5: Results"

if [ -f "$DEMO_DIR/best_refactored.py" ]; then
    print_success "Refactoring completed successfully!"
    
    echo -e "${BOLD}Best refactored version:${NC}"
    echo "  File: best_refactored.py"
    echo "  Size: $(wc -l < "$DEMO_DIR/best_refactored.py") lines"
    
    echo -e "\n${BOLD}Improvement summary:${NC}"
    echo "  Original: $(wc -l < "$DEMO_DIR/legacy_code/data_processor.py") lines"
    echo "  Refactored: $(wc -l < "$DEMO_DIR/best_refactored.py") lines"
    
    # Show first few lines of refactored code
    echo -e "\n${BOLD}Sample of refactored code:${NC}"
    head -30 "$DEMO_DIR/best_refactored.py" | cat -n
else
    print_error "Refactoring did not produce valid output"
fi

# Step 6: Log Files
print_section "STEP 6: Log Files"

echo -e "${BOLD}Generated log files:${NC}"
echo "  • claude_autonomous.log - Detailed autonomous workflow logs"
echo "  • claude-autonomous-output.log - Full demo output"
echo "  • docker-build.log - Docker build output"
echo "  • docker-run.log - Container runtime logs"

echo -e "\n${CYAN}Log summary:${NC}"
if [ -f "$DEMO_DIR/claude_autonomous.log" ]; then
    echo "  claude_autonomous.log: $(wc -l < "$DEMO_DIR/claude_autonomous.log") lines"
fi
if [ -f "$DEMO_DIR/claude-autonomous-output.log" ]; then
    echo "  claude-autonomous-output.log: $(wc -l < "$DEMO_DIR/claude-autonomous-output.log") lines"
fi

# Summary
print_section "SUMMARY"

if [ -f "$DEMO_DIR/best_refactored.py" ]; then
    print_success "Claude Code autonomous demo completed successfully!"
    echo ""
    echo -e "${BOLD}Achievements:${NC}"
    echo "  • Autonomous refactoring with Claude Code"
    echo "  • Multi-criteria validation (vallm + runtime tests)"
    echo "  • Iterative improvement loop"
    echo "  • Code quality and security verification"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo "  • Review best_refactored.py"
    echo "  • Compare with legacy_code/data_processor.py"
    echo "  • Check claude_autonomous.log for detailed trace"
    echo "  • Examine iteration files (refactored_v*.py)"
else
    print_error "Demo completed with issues"
    echo ""
    echo -e "${BOLD}Check logs for details:${NC}"
    echo "  tail -100 claude_autonomous.log"
    echo "  docker logs $CONTAINER_NAME"
fi

# Cleanup
print_section "CLEANUP"

echo -e "${CYAN}To stop and remove the container:${NC}"
echo "  docker stop $CONTAINER_NAME"
echo "  docker rm $CONTAINER_NAME"

echo -e "\n${CYAN}To run the demo again:${NC}"
echo "  ./run.sh"

echo -e "\n${CYAN}To enter the container:${NC}"
echo "  docker exec -it $CONTAINER_NAME bash"

echo -e "\n${GREEN}Demo complete!${NC}"
