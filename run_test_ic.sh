#!/bin/bash
set -e
set -x

IMAGE_NAME=kybra-simple-vault-test

# Check if the ledger files are already downloaded
LEDGER_DIR="tests/ledger_suite_icrc"
mkdir -p $LEDGER_DIR

# Download the ledger files if they don't exist
if [ ! -f "$LEDGER_DIR/ic-icrc1-ledger.wasm" ]; then
    echo "Downloading ledger files..."
    curl -L -o "$LEDGER_DIR/ic-icrc1-ledger.wasm.gz" https://github.com/dfinity/ic/releases/download/ledger-suite-icrc-2025-02-27/ic-icrc1-ledger.wasm.gz
    gunzip "$LEDGER_DIR/ic-icrc1-ledger.wasm.gz"
    curl -L -o "$LEDGER_DIR/ledger.did" https://github.com/dfinity/ic/releases/download/ledger-suite-icrc-2025-02-27/ledger.did
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Run the tests in a Docker container
echo "Running IC tests in Docker container..."
docker run --rm $IMAGE_NAME || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All tests passed successfully!"