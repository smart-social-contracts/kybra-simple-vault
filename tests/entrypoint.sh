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

# Get the current principal
PRINCIPAL=$(dfx identity get-principal)

# Deploy the ledger canister with explicit arguments
echo "Deploying ckbtc_ledger canister..."
dfx deploy --no-wallet ckbtc_ledger --argument="(variant { Init = record { minting_account = record { owner = principal \"$PRINCIPAL\"; subaccount = null }; transfer_fee = 10; token_symbol = \"ckBTC\"; token_name = \"ckBTC Test\"; decimals = opt 8; metadata = vec {}; initial_balances = vec { record { record { owner = principal \"$PRINCIPAL\"; subaccount = null }; 1_000_000_000 } }; feature_flags = opt record { icrc2 = true }; archive_options = record { num_blocks_to_archive = 1000; trigger_threshold = 2000; controller_id = principal \"$PRINCIPAL\" } } })"

# Get the ledger canister ID
LEDGER_ID=$(dfx canister id ckbtc_ledger)

# Deploy the indexer canister with the ledger ID
echo "Deploying indexer canister..."
dfx deploy --no-wallet ckbtc_indexer --argument="(opt variant { Init = record { ledger_id = principal \"$LEDGER_ID\"; retrieve_blocks_from_ledger_interval_seconds = opt 1 } })"

# Deploy the vault canister
echo "Deploying vault canister..."
dfx deploy vault

# Set the ckBTC ledger canister principal in the vault canister
echo "Setting ckBTC ledger canister principal in vault..."
INDEXER_ID=$(dfx canister id ckbtc_indexer)
dfx canister call vault set_canister '("ckBTC ledger", principal "'"$LEDGER_ID"'")'
dfx canister call vault set_canister '("ckBTC indexer", principal "'"$INDEXER_ID"'")'

# Run tests against the vault canister
echo "Running IC integration tests..."
python tests/test_ic_vault.py

# Check the exit code of the tests
if [ $? -ne 0 ]; then
    echo "❌ IC integration tests failed"
    # sleep 999999
    # dfx stop
    exit 1
    
fi

# Successfully complete the test
echo "Canister deployment tests passed successfully!"

# echo "Stopping dfx..."
# dfx stop

echo "All tests passed successfully!"

# sleep 999999