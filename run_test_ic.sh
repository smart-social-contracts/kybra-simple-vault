#!/bin/bash
set -e
set -x

IMAGE_NAME=kybra-simple-vault-test

tests/download_ledger.sh

# Build the Docker image
echo "Building Docker image..."
docker build --no-cache -t $IMAGE_NAME .

# Run the tests in a Docker container
echo "Running IC tests in Docker container..."
docker run --rm $IMAGE_NAME --entrypoint tests/entrypoint.sh || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All tests passed successfully!"