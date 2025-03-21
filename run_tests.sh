#!/bin/bash

# Exit on error and undefined variables, and print commands
set -eux

# Get the absolute path to the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function for logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "ERROR: $1"
    exit 1
}

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    handle_error "Docker is not installed or not in PATH"
fi

# Pull the latest image
log "Pulling the latest image..."
if ! docker pull ghcr.io/smart-social-contracts/icp-dev-env:latest; then
    handle_error "Failed to pull the Docker image"
fi

# Run the container with mounted volumes
log "Starting the container..."
docker run --rm -it \
    -v "${PROJECT_ROOT}/src:/app/src" \
    -v "${PROJECT_ROOT}/tests:/app/tests" \
    -v "${PROJECT_ROOT}/entrypoint.sh:/app/entrypoint.sh" \
    --entrypoint "/app/entrypoint.sh" \
    ghcr.io/smart-social-contracts/icp-dev-env:latest

log "Container execution completed"
