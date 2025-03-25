#!/bin/bash
set -e
set -x

IMAGE_NAME=kybra-simple-vault-test

docker build -t $IMAGE_NAME .

echo "Running tests..."
docker run --rm $IMAGE_NAME || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All tests passed successfully!"