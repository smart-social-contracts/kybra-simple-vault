#!/bin/bash
set -e
set -x

IMAGE_ADDRESS="ghcr.io/smart-social-contracts/icp-dev-env:latest"

echo "Running tests..."
docker run --rm \
    -v "${PWD}/src/vault:/app/src" \
    -v "${PWD}/src/main.py:/app/src/main.py" \
    -v "${PWD}/src/tester.py:/app/src/tester.py" \
    -v "${PWD}/dfx.json:/app/dfx.json" \
    -v "${PWD}/entrypoint.sh:/app/entrypoint.sh" \
    --entrypoint "/app/entrypoint.sh" \
    $IMAGE_ADDRESS || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All tests passed successfully!"