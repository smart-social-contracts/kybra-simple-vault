#!/bin/bash
set -e
set -x

# Get the test type from the first parameter, or run 'general' and 'transactions' tests if not provided
if [ -z "$1" ]; then
    TEST_TYPES=("general" "transactions")
else
    TEST_TYPES=("$1")
fi

IMAGE_NAME=kybra-simple-vault-test

# Download test artifacts
echo "Downloading test artifacts..."
./download_test_artifacts.sh

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Run the tests in a Docker container with the specified test type(s)
for TEST_TYPE in "${TEST_TYPES[@]}"; do
    echo "Running IC tests in Docker container for test type: $TEST_TYPE..."
    docker run --rm $IMAGE_NAME $TEST_TYPE || {
        echo "❌ Tests failed for $TEST_TYPE"
        exit 1
    }
done

echo "✅ All tests passed successfully!"