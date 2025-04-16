#!/bin/bash
set -e

echo ">>> Extracting version from setup.cfg..."
VERSION=$(grep -m1 '^version =' setup.cfg | cut -d '=' -f2 | tr -d ' ')
echo ">>> Version is: $VERSION"

echo ">>> Building vault canister WASM in Docker using version $VERSION..."
IMAGE_NAME=${IMAGE_NAME:-kybra-simple-vault-test}

# Ensure the Docker image exists
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
  echo "Docker image $IMAGE_NAME not found. Building it now..."
  docker build -t $IMAGE_NAME .
fi

echo ">>> Building vault canister WASM in Docker using version $VERSION and image $IMAGE_NAME..."

# Detect if running in a TTY (local terminal) or not (CI) and add -t only if a TTY is present
DOCKER_TTY=""
if [ -t 1 ]; then
  DOCKER_TTY="-t"
fi

docker run --rm -i $DOCKER_TTY \
  --entrypoint bash \
  -v "$(pwd)":/app \
  -w /app \
  $IMAGE_NAME \
  -c "set -x; \
    echo '>>> Starting local IC replica...'; \
    dfx start --clean --background; \
    echo '>>> Creating canister...'; \
    dfx canister create vault; \
    echo '>>> Building canister...'; \
    dfx build vault; \
    echo '>>> Copying WASM...'; \
    cp .kybra/vault/vault.wasm /app/vault_${VERSION}.wasm; \
  "


echo ">>> Build complete. vault_${VERSION}.wasm is ready."

