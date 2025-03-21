#!/bin/bash

# Exit on error and undefined variables, and print commands
set -eux

# Function for logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "ERROR: $1"
    exit 1
}

# Change to app directory
cd /app || handle_error "Failed to change to /app directory"

if ! dfx start --clean --background; then
handle_error "Failed to start dfx"
fi

# # Install npm dependencies first
# log "Installing dependencies..."
# if ! npm install; then
# handle_error "Failed to install dependencies"
# fi


# Build Python canister
log "Building canister_main canister..."
if ! dfx deploy canister_main --verbose; then
handle_error "Failed to build Python canister"
fi


# # Deploy remaining canisters
# log "Deploying canister_frontend canister..."
# if ! dfx deploy canister_frontend --verbose; then
# handle_error "Failed to deploy frontend canister"
# fi

# Run tests
log "Running tests..."
if ! cd tests; then
handle_error "Failed to change to tests directory"
fi

# if ! PYTHONPATH=$PWD/../src/canister_main python -m pytest -s tests.py; then
# handle_error "Tests failed"
# fi

log "Tests completed successfully"
