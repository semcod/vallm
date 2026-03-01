#!/bin/bash

# Vallm Examples Runner
# This script runs all examples sequentially and generates analysis reports

set -e  # Exit on any error

echo "🚀 Running Vallm Examples"
echo "========================"

# List of example directories in order
EXAMPLES=(
    "01_basic_validation"
    "02_ast_comparison" 
    "03_security_check"
    "04_graph_analysis"
    "05_llm_semantic_review"
    "06_multilang_validation"
    "07_multi_language"
    "08_code2llm_integration"
    "09_code2logic_integration"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run an example
run_example() {
    local example_dir=$1
    echo -e "\n${BLUE}📁 Running example: ${example_dir}${NC}"
    echo "----------------------------------------"
    
    if [ ! -d "$example_dir" ]; then
        echo -e "${RED}❌ Example directory $example_dir not found${NC}"
        return 1
    fi
    
    if [ ! -f "$example_dir/main.py" ]; then
        echo -e "${RED}❌ main.py not found in $example_dir${NC}"
        return 1
    fi
    
    # Change to example directory and run
    cd "$example_dir"
    
    # Clean any previous .vallm folder
    if [ -d ".vallm" ]; then
        rm -rf .vallm
    fi
    
    echo -e "${YELLOW}▶️  Running python main.py${NC}"
    
    # Run the example and capture output
    if python main.py 2>&1; then
        echo -e "${GREEN}✅ Example $example_dir completed successfully${NC}"
        
        # Check if analysis data was generated
        if [ -d ".vallm" ]; then
            echo -e "${GREEN}📊 Analysis data generated in .vallm/ folder${NC}"
            ls -la .vallm/
        else
            echo -e "${YELLOW}⚠️  No .vallm folder generated${NC}"
        fi
    else
        echo -e "${RED}❌ Example $example_dir failed${NC}"
        cd ..
        return 1
    fi
    
    cd ..
    echo ""
}

# Main execution
echo -e "${BLUE}Starting sequential execution of ${#EXAMPLES[@]} examples...${NC}"

total_start_time=$(date +%s)
failed_examples=()

for example in "${EXAMPLES[@]}"; do
    start_time=$(date +%s)
    
    if ! run_example "$example"; then
        failed_examples+=("$example")
    fi
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    echo -e "${BLUE}⏱️  Time taken: ${duration}s${NC}"
    echo "========================================"
done

total_end_time=$(date +%s)
total_duration=$((total_end_time - total_start_time))

# Final summary
echo -e "\n${BLUE}📋 EXECUTION SUMMARY${NC}"
echo "========================"
echo -e "${BLUE}Total time: ${total_duration}s${NC}"
echo -e "${BLUE}Examples run: ${#EXAMPLES[@]}${NC}"

if [ ${#failed_examples[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All examples completed successfully!${NC}"
else
    echo -e "${RED}❌ Failed examples (${#failed_examples[@]}):${NC}"
    for failed in "${failed_examples[@]}"; do
        echo -e "${RED}   - $failed${NC}"
    done
fi

# Generate overall summary
echo -e "\n${BLUE}📊 ANALYSIS DATA SUMMARY${NC}"
echo "=========================="

for example in "${EXAMPLES[@]}"; do
    if [ -d "$example/.vallm" ]; then
        echo -e "${GREEN}📁 $example:${NC}"
        ls -1 "$example/.vallm/" | sed 's/^/   - /'
    else
        echo -e "${YELLOW}📁 $example: No analysis data${NC}"
    fi
done

echo -e "\n${GREEN}🎉 Vallm examples runner completed!${NC}"

# Exit with error code if any examples failed
if [ ${#failed_examples[@]} -gt 0 ]; then
    exit 1
fi
