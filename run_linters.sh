#!/bin/bash
# Simple script to run all linters from CI workflow locally
# Usage: ./run_linters.sh [--fix]
#   --fix    Apply fixes automatically when possible (black, isort)

# Exit on first error
set -e

# Check if we should fix issues or just check
FIX_MODE=false
if [ "$1" == "--fix" ]; then
    FIX_MODE=true
    echo "Running linters in FIX mode..."
else
    echo "Running linters in CHECK mode (use --fix to auto-format)..."
fi

# Check/fix formatting with black
echo "Running black..."
if [ "$FIX_MODE" = true ]; then
    black src tests
else
    black src tests --check
fi

# Check/fix imports with isort
echo "Running isort..."
if [ "$FIX_MODE" = true ]; then
    isort src tests
else
    isort src tests --check-only
fi

# Lint with flake8 (no auto-fix available)
echo "Running flake8..."
flake8 src tests --ignore=E501,W391,W503,F405,F403,F401,E722,F811,E704

# Type check with mypy (no auto-fix available)
echo "Running mypy..."
mypy src tests

echo "All linters completed successfully!"
