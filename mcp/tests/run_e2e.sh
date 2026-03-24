#!/bin/bash
# MCP Vallm E2E Test Runner

set -e

echo "🧪 MCP Vallm E2E Test Runner"
echo "============================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run from project root."
    exit 1
fi

print_status "Found pyproject.toml - in correct directory"

# Run quick tests first
echo ""
echo "🔍 Running quick tests..."
if python3 mcp/tests/quick_test.py; then
    print_status "Quick tests passed"
else
    print_error "Quick tests failed"
    exit 1
fi

# Build Docker image
echo ""
echo "🐳 Building Docker image..."
if docker build -t vallm-mcp-test -f mcp/tests/Dockerfile.test .; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Run Docker tests
echo ""
echo "🏃 Running Docker e2e tests..."
if docker run --rm vallm-mcp-test; then
    print_status "Docker e2e tests passed"
else
    print_error "Docker e2e tests failed"
    exit 1
fi

# Optional: Run docker-compose tests
if [ "$1" = "--compose" ]; then
    echo ""
    echo "🔄 Running docker-compose tests..."

    # Run compose tests using the same container-side runner
    if docker-compose -f mcp/tests/docker-compose.yml up --build --abort-on-container-exit; then
        print_status "Docker-compose tests passed"
    else
        print_error "Docker-compose tests failed"
        exit 1
    fi

    # Clean up
    docker-compose -f mcp/tests/docker-compose.yml down
fi

# Clean up Docker image
echo ""
echo "🧹 Cleaning up..."
docker rmi vallm-mcp-test 2>/dev/null || true

print_status "All tests completed successfully! 🎉"
