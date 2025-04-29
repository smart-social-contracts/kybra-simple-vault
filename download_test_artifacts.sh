#!/bin/bash
set -e
set -x

LEDGER_SUITE_DIR="tests/artifacts/ledger_suite_icrc"
LEDGER_SUITE_URL="https://github.com/dfinity/ic/releases/download/ledger-suite-icrc-2025-02-27"
mkdir -p $LEDGER_SUITE_DIR

# Download the ledger files if they don't exist
if [ ! -f "$LEDGER_SUITE_DIR/ledger.wasm" ]; then
    echo "Downloading ledger wasm tarball file..."
    curl -L -o "$LEDGER_SUITE_DIR/ledger.wasm.gz" $LEDGER_SUITE_URL/ic-icrc1-ledger.wasm.gz
    gunzip "$LEDGER_SUITE_DIR/ledger.wasm.gz"
else
    echo "Ledger wasm tarball file already downloaded"
fi

if [ ! -f "$LEDGER_SUITE_DIR/ledger.did" ]; then
    echo "Downloading ledger candid file..."
    curl -L -o "$LEDGER_SUITE_DIR/ledger.did" $LEDGER_SUITE_URL/ledger.did
else
    echo "Ledger candid file already downloaded"
fi

# Download the indexer files if they don't exist
if [ ! -f "$LEDGER_SUITE_DIR/indexer.wasm" ]; then
    echo "Downloading indexer wasm tarball file..."
    curl -L -o "$LEDGER_SUITE_DIR/indexer.wasm.gz" $LEDGER_SUITE_URL/ic-icrc1-index-ng.wasm.gz
    gunzip "$LEDGER_SUITE_DIR/indexer.wasm.gz"
else
    echo "Indexer wasm tarball file already downloaded"
fi

if [ ! -f "$LEDGER_SUITE_DIR/indexer.did" ]; then
    echo "Downloading indexer candid file..."
    curl -L -o "$LEDGER_SUITE_DIR/indexer.did" $LEDGER_SUITE_URL/index-ng.did
else
    echo "Indexer candid file already downloaded"
fi
