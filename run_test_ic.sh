#!/bin/bash
set -e
set -x

# Directory where the tests are located
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start the replica, deploy the ledger canister, and configure it
dfx start --background --clean

# Deploy the ledger canister and set it up
echo "Deploying ledger canister..."
dfx deploy --no-wallet ledger_suite_icrc
dfx canister call ledger_suite_icrc setup '()'

# Deploy the actual vault canister
echo "Deploying vault canister..."
dfx deploy vault

# Run tests against the vault canister
echo "Running IC integration tests..."

# Test 1: Check canister balance
echo "Testing balance functionality..."
BALANCE=$(dfx canister call vault get_canister_balance)
echo "Vault balance: $BALANCE"

# Test 2: Test transfers (first need to mint some tokens to the canister)
echo "Testing transfer functionality..."
# Create a test account
TEST_ACCOUNT="rwlgt-iiaaa-aaaaa-aaaaa-cai"

# Get the vault canister ID
VAULT_ID=$(dfx canister id vault)

# Mint some tokens to the vault (using the ledger canister)
echo "Minting tokens to the vault..."
dfx canister call ledger_suite_icrc test_mint "($VAULT_ID, 1000000)" # 1 token with 6 decimals

# Get initial balance
INITIAL_BALANCE=$(dfx canister call vault get_canister_balance)
echo "Initial balance: $INITIAL_BALANCE"

# Send tokens from the vault
echo "Sending tokens from vault..."
dfx canister call vault do_transfer "($TEST_ACCOUNT, 500000)"

# Get final balance
FINAL_BALANCE=$(dfx canister call vault get_canister_balance)
echo "Final balance: $FINAL_BALANCE"

# Verify the balance decreased
if (( $INITIAL_BALANCE - $FINAL_BALANCE >= 500000 )); then
    echo "Transfer test passed!"
else
    echo "Transfer test failed!"
    exit 1
fi

# Stop dfx
dfx stop

echo "✅ All tests passed successfully!"