#!/bin/bash
set -e
set -x

IMAGE_NAME=kybra-simple-vault-test

tests/download_ledger.sh

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .  # --no-cache 

# Run the tests in a Docker container
echo "Running IC tests in Docker container..."

docker run --rm --entrypoint tests/entrypoint.sh $IMAGE_NAME || {
    echo "❌ Tests failed"
    sleep 999999
    exit 1
}

echo "✅ All tests passed successfully!"