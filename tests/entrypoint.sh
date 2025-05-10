#!/bin/bash
set -e
set -x

# Start dfx in the background (only if not already running)
echo "Checking if dfx is already running..."
if ! dfx ping &>/dev/null; then
    echo "Starting dfx..."
    dfx start --background --clean
else
    echo "dfx is already running"
fi

# Get the test type from the first parameter, default to "general" if not provided
TEST_TYPE=${1:-general}
echo "Running tests for type: $TEST_TYPE"

echo "Running IC integration tests..."
python -u tests/run_test_$TEST_TYPE.py

# Check the exit code of the tests
if [ $? -ne 0 ]; then
    echo "❌ IC integration tests failed"
    exit 1
fi

echo "All tests passed successfully!"