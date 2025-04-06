#!/bin/bash
set -e
set -x

echo "Running tests..."

exit_code=0

TEST_IDS=('initialization' 'transaction_processing' 'balance_tracking' 'sync_recovery' 'reset' 'admin')

# Use absolute paths to ensure imports work properly
PROJECT_ROOT="$(pwd)"
TEST_PYTHON_PATH="$PROJECT_ROOT:$PROJECT_ROOT/src:$PROJECT_ROOT/src/vault"

# Check if a specific test ID is provided as an argument
if [ "$1" ]; then
  if [[ " ${TEST_IDS[@]} " =~ " $1 " ]]; then
    echo "Running test $1..."
    PYTHONPATH=$TEST_PYTHON_PATH python tests/test_$1.py || exit_code=1
    exit $exit_code
  else
    echo "Invalid test ID: $1"
    echo "Valid test IDs are: ${TEST_IDS[@]}"
    exit 1
  fi
fi

for TEST_ID in "${TEST_IDS[@]}"; do
  echo "Running test $TEST_ID..."
  PYTHONPATH=$TEST_PYTHON_PATH python tests/test_${TEST_ID}.py || exit_code=1
done

if [ $exit_code -eq 0 ]; then
  echo -e "\033[0;32mAll tests passed successfully!\033[0m"
else
  echo -e "\033[0;31mSome tests failed. Please check the logs.\033[0m"
fi

exit $exit_code
