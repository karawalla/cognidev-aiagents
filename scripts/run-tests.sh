#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting test execution...${NC}"

# Create test reports directory if it doesn't exist
mkdir -p test-reports

# Ensure we're in the project root
cd "$(dirname "$0")/.." || exit 1

# Clean up any previous test containers
echo -e "${YELLOW}Cleaning up previous test containers...${NC}"
docker-compose -f docker/docker-compose.yml down

# Build and run tests
echo -e "${YELLOW}Building and running tests...${NC}"
docker-compose -f docker/docker-compose.yml up --build test

# Check if tests were successful
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Tests completed successfully!${NC}"
else
    echo -e "${RED}Tests failed with exit code $TEST_EXIT_CODE${NC}"
fi

# Function to open URL in browser
open_url() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "$1"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open "$1" &>/dev/null
    else
        echo -e "${YELLOW}Please open the following URL in your browser:${NC}"
        echo "$1"
    fi
}

# Wait for reports to be generated
echo -e "${YELLOW}Opening test reports in browser...${NC}"
sleep 2

# Open HTML report and coverage report
REPORT_PATH="$(pwd)/test-reports/report.html"
COVERAGE_PATH="$(pwd)/test-reports/coverage/index.html"

if [ -f "$REPORT_PATH" ]; then
    echo -e "${GREEN}Opening test report...${NC}"
    open_url "file://$REPORT_PATH"
else
    echo -e "${RED}Test report not found at $REPORT_PATH${NC}"
fi

if [ -f "$COVERAGE_PATH" ]; then
    echo -e "${GREEN}Opening coverage report...${NC}"
    open_url "file://$COVERAGE_PATH"
else
    echo -e "${RED}Coverage report not found at $COVERAGE_PATH${NC}"
fi

# Exit with the test exit code
exit $TEST_EXIT_CODE
