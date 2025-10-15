#!/bin/bash
# Type checking script for SeleniumPelican
# Usage: ./scripts/type_check.sh [--report]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${CYAN}🔍 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we should generate report
GENERATE_REPORT=false
if [ "$1" = "--report" ]; then
    GENERATE_REPORT=true
fi

# Main type checking
print_info "Running mypy type checker..."

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Not in virtual environment, using uv run"
    MYPY_CMD="uv run mypy"
else
    MYPY_CMD="mypy"
fi

# Run mypy on src directory
if $MYPY_CMD src/ --config-file pyproject.toml; then
    print_success "Type check completed with no errors"
    EXIT_CODE=0
else
    print_error "Type check failed - please fix the errors above"
    EXIT_CODE=1
fi

# Generate reports if requested
if [ "$GENERATE_REPORT" = true ]; then
    print_info "Generating type coverage reports..."

    # Generate HTML report
    $MYPY_CMD src/ --config-file pyproject.toml --html-report mypy-html --no-error-summary 2>/dev/null || true

    # Generate text report
    $MYPY_CMD src/ --config-file pyproject.toml --txt-report mypy-report --no-error-summary 2>/dev/null || true

    if [ -d "mypy-html" ]; then
        print_success "HTML report generated at: mypy-html/index.html"
    fi

    if [ -d "mypy-report" ]; then
        print_success "Text report generated at: mypy-report/"
    fi
fi

exit $EXIT_CODE
