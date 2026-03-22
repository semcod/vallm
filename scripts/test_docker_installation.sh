#!/bin/bash
# Docker installation test script for vallm across multiple systems

set -e

echo "🐳 Testing vallm installation across multiple Docker images..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to test Docker image
test_image() {
    local image_name=$1
    local stage_name=$2
    
    echo "Testing $stage_name..."
    
    # Build the specific stage
    if docker build --target $stage_name -t vallm-test-$stage_name -f Dockerfile.test .; then
        print_status "$stage_name built successfully"
        
        # Run tests in the container
        if docker run --rm vallm-test-$stage_name vallm --help > /dev/null 2>&1; then
            print_status "$stage_name: vallm --help works"
        else
            print_error "$stage_name: vallm --help failed"
            return 1
        fi
        
        if docker run --rm vallm-test-$stage_name vallm info > /dev/null 2>&1; then
            print_status "$stage_name: vallm info works"
        else
            print_error "$stage_name: vallm info failed"
            return 1
        fi
        
        # Test basic validation
        docker run --rm vallm-test-$stage_name sh -c "
            echo 'def hello(): return \"world\"' > test.py
            vallm validate --file test.py
        " && print_status "$stage_name: basic validation works" || print_error "$stage_name: basic validation failed"
        
        # Test batch validation
        docker run --rm vallm-test-$stage_name sh -c "
            mkdir -p test_project
            echo 'def func1(): pass' > test_project/file1.py
            echo 'def func2(): pass' > test_project/file2.py
            vallm batch test_project --recursive
        " && print_status "$stage_name: batch validation works" || print_error "$stage_name: batch validation failed"
        
    else
        print_error "$stage_name build failed"
        return 1
    fi
    
    echo ""
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if Dockerfile.test exists
if [ ! -f "Dockerfile.test" ]; then
    print_error "Dockerfile.test not found"
    exit 1
fi

# Test each stage
test_image "ubuntu:22.04" "ubuntu-22"
test_image "ubuntu:24.04" "ubuntu-24"
test_image "debian:bookworm" "debian-12"
test_image "alpine:3.19" "alpine"
test_image "fedora:39" "fedora-39"
test_image "quay.io/centos/centos:stream9" "centos-9"
test_image "python:3.11-slim" "python-slim"
test_image "python:3.11-alpine" "python-alpine"

echo "🎉 Docker installation tests completed!"

# Optional: Clean up test images
read -p "Do you want to clean up test images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleaning up test images..."
    docker rmi vallm-test-ubuntu-22 vallm-test-ubuntu-24 vallm-test-debian-12 vallm-test-alpine vallm-test-fedora-39 vallm-test-centos-9 vallm-test-python-slim vallm-test-python-alpine 2>/dev/null || true
    print_status "Cleanup completed"
fi
