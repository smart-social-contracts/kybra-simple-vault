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

# Get the current principal
PRINCIPAL=$(dfx identity get-principal)

# Deploy the ledger canister with explicit arguments
echo "Deploying ckbtc_ledger canister..."
dfx deploy --no-wallet ckbtc_ledger --argument="(variant { Init = record { minting_account = record { owner = principal \"$PRINCIPAL\"; subaccount = null }; transfer_fee = 10; token_symbol = \"ckBTC\"; token_name = \"ckBTC Test\"; decimals = opt 8; metadata = vec {}; initial_balances = vec { record { record { owner = principal \"$PRINCIPAL\"; subaccount = null }; 1_000_000_000 } }; feature_flags = opt record { icrc2 = true }; archive_options = record { num_blocks_to_archive = 1000; trigger_threshold = 2000; controller_id = principal \"$PRINCIPAL\" } } })"

# Deploy the vault canister with explicit init arguments
CKBTC_PRINCIPAL=$(dfx canister id ckbtc_ledger)
VAULT_CANISTER_ID=$(dfx canister id ckbtc_ledger)
echo "Deploying vault canister with arguments: (opt \"$VAULT_CANISTER_ID\", opt principal \"$CKBTC_PRINCIPAL\", opt principal \"$PRINCIPAL\", 0)"
dfx deploy vault --argument="(opt \"$VAULT_CANISTER_ID\", opt principal \"$CKBTC_PRINCIPAL\", opt principal \"$PRINCIPAL\", 0)" 

# Run tests against the vault canister
echo "Running IC integration tests..."
python /app/test_ic_vault_canister.py

# Check the exit code of the tests
if [ $? -ne 0 ]; then
    echo "❌ IC integration tests failed"
    dfx stop
    exit 1
fi


# Successfully complete the test
echo "Canister deployment tests passed successfully!"


echo "Stopping dfx..."
dfx stop

echo "All tests passed successfully!"