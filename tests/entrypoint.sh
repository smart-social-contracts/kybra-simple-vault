#!/bin/bash
set -e
set -x

# Start dfx in the background
echo "Starting dfx..."
dfx start --background --clean

# Copy the ledger wasm and did files to the right location
echo "Setting up ledger suite..."
mkdir -p .dfx/local/canisters
cp /app/ledger_suite_icrc/ic-icrc1-ledger.wasm ledger_suite_icrc.wasm
cp /app/ledger_suite_icrc/ledger.did ledger_suite_icrc.did

# Deploy the ledger canister
echo "Deploying ckbtc_ledger canister..."
dfx deploy --no-wallet ckbtc_ledger
dfx canister call ckbtc_ledger setup '()'

# Deploy the vault canister
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
dfx canister call ckbtc_ledger test_mint "($VAULT_ID, 1000000)" # 1 token with 6 decimals

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
if [[ "$INITIAL_BALANCE" == *"1000000"* && "$FINAL_BALANCE" == *"500000"* ]]; then
    echo "Transfer test passed!"
else
    echo "Transfer test failed!"
    dfx stop
    exit 1
fi

echo "Stopping dfx..."
dfx stop

echo "All tests passed successfully!"