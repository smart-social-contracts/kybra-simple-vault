#!/bin/bash
set -e
set -x

IMAGE_NAME=kybra-simple-vault-test

# Download test artifacts
echo "Downloading test artifacts..."
./download_test_artifacts.sh

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Run the tests in a Docker container
echo "Running IC tests in Docker container..."
docker run --rm $IMAGE_NAME || {
    echo "❌ Tests failed"
    sleep 999999
    exit 1
}

echo "✅ All tests passed successfully!"