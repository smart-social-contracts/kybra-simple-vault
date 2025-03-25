#!/bin/bash
set -e
set -x

# Start dfx in the background
echo "Starting dfx..."
dfx start --background --clean

# Deploy the test canister
echo "Deploying test canister..."
dfx deploy

# # Call greet and check output
# echo "Testing greet function..."
# GREET_RESULT=$(dfx canister call test greet)
# if [ "$GREET_RESULT" != '("Hello!")' ]; then
#   echo "Error: greet function returned unexpected result: $GREET_RESULT"
#   dfx stop
#   exit 1
# else
#   echo "greet function test passed!"
# fi

# Define a list of test identifiers
TEST_IDS=('parse_candid')


# Loop through each test identifier
for TEST_ID in "${TEST_IDS[@]}"; do
  echo "Testing test_${TEST_ID} module..."
  TEST_RESULT=$(dfx canister call test run_test ${TEST_ID})
  if [ "$TEST_RESULT" != '(0 : int)' ]; then
    echo "Error: test_${TEST_ID}.run() function returned unexpected result: $TEST_RESULT"
    dfx stop
    exit 1 
  else
    echo "test_${TEST_ID}.run() function test passed!"
  fi
done

echo "Stopping dfx..."
dfx stop

echo "All done!"