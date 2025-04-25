#!/bin/bash
set -e
set -x

sleep 999999
# Start dfx in the background
echo "Starting dfx...";
dfx start --background --clean

# Run tests against the vault canister (now includes deployment)
echo "Running IC integration tests..."
python tests/test_ic_integration.py

# Check the exit code of the tests
if [ $? -ne 0 ]; then
  echo "❌ Tests failed"
  sleep 99999
  exit 1
else
  echo "✅ All tests passed"
  exit 0
fi