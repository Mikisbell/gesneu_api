#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TEST_PATH="tests"
PARALLEL_WORKERS=4
COVERAGE_THRESHOLD=90

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --unit)
      TEST_PATH="tests/unit"
      shift
      ;;
    --integration)
      TEST_PATH="tests/integration"
      shift
      ;;
    --property)
      TEST_PATH="tests/property_based"
      shift
      ;;
    --path=*)
      TEST_PATH="${1#*=}"
      shift
      ;;
    --workers=*)
      PARALLEL_WORKERS="${1#*=}"
      shift
      ;;
    --coverage-threshold=*)
      COVERAGE_THRESHOLD="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo -e "${YELLOW}Running tests in ${TEST_PATH} with ${PARALLEL_WORKERS} workers...${NC}"

# Create coverage directory if it doesn't exist
mkdir -p htmlcov

# Run pytest with coverage
PYTHONPATH=. \
pytest $TEST_PATH \
  --cov=ges_neu_api \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  --cov-fail-under=$COVERAGE_THRESHOLD \
  -n $PARALLEL_WORKERS \
  -v \
  --asyncio-mode=auto \
  --durations=10 \
  --color=yes \
  --cov-append \
  --cov-branch \
  --cov-context=test \
  --cov-report=xml:coverage.xml \
  --junitxml=junit/test-results.xml \
  --log-level=INFO

# Check if tests passed
if [ $? -eq 0 ]; then
  echo -e "${GREEN}🎉 All tests passed!${NC}"
  
  # Open coverage report in default browser
  if command -v xdg-open > /dev/null; then
    xdg-open htmlcov/index.html
  elif command -v open > /dev/null; then
    open htmlcov/index.html
  fi
  
  exit 0
else
  echo -e "${YELLOW}❌ Some tests failed. Check the report above for details.${NC}"
  exit 1
fi
