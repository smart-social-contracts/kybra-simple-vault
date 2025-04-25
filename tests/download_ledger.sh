#!/bin/bash
set -e
set -x

LEDGER_DIR="tests/artifacts/ledger_suite_icrc"
LEDGER_URL="https://github.com/dfinity/ic/releases/download/ledger-suite-icrc-2025-02-27"
mkdir -p $LEDGER_DIR

# Download the ledger files if they don't exist
if [ ! -f "$LEDGER_DIR/ledger.wasm" ]; then
    echo "Downloading ledger wasm tarball file..."
    curl -L -o "$LEDGER_DIR/ledger.wasm.gz" $LEDGER_URL/ic-icrc1-ledger.wasm.gz
    gunzip "$LEDGER_DIR/ledger.wasm.gz"
else
    echo "Ledger wasm tarball file already downloaded"
fi

if [ ! -f "$LEDGER_DIR/ledger.did" ]; then
    echo "Downloading ledger candid file..."
    curl -L -o "$LEDGER_DIR/ledger.did" $LEDGER_URL/ledger-suite-icrc-2025-02-27/ledger.did
else
    echo "Ledger candid file already downloaded"
fi