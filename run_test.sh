#!/bin/bash
set -e
set -x

# Get the test type from the first parameter, default to "general" if not provided
TEST_TYPE=${1:-general}
IMAGE_NAME=kybra-simple-vault-test

# Download test artifacts
echo "Downloading test artifacts..."
./download_test_artifacts.sh

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Run the tests in a Docker container with the specified test type
echo "Running IC tests in Docker container for test type: $TEST_TYPE..."
docker run --rm $IMAGE_NAME $TEST_TYPE || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All tests passed successfully!"