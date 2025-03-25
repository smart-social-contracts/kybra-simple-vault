#!/bin/bash
set -e
set -x

echo "Running tests..."

exit_code=0

TEST_IDS=('parse_candid')

# Check if a specific test ID is provided as an argument
if [ "$1" ]; then
  if [[ " ${TEST_IDS[@]} " =~ " $1 " ]]; then
    echo "Running test $1..."
    PYTHONPATH="src/vault:tests/src/vault" python tests/src/vault/tests/test_$1.py || exit_code=1
    exit $exit_code
  else
    echo "Invalid test ID: $1"
    echo "Valid test IDs are: ${TEST_IDS[@]}"
    exit 1
  fi
fi

for TEST_ID in "${TEST_IDS[@]}"; do
  PYTHONPATH="src/vault:tests/src/vault" python tests/src/vault/tests/test_${TEST_ID}.py || exit_code=1
done

if [ $exit_code -eq 0 ]; then
  echo -e "\033[0;32mAll tests passed successfully!\033[0m"
else
  echo -e "\033[0;31mSome tests failed. Please check the logs.\033[0m"
fi

exit $exit_code
