#!/bin/bash

# Exit on error
set -e

LIB_NAME="kybra_simple_db"

# Install the library
pip install $LIB_NAME

# Use Python to find the path to the library
LIB_PATH=$(python -c "import $LIB_NAME; import os; print(os.path.dirname($LIB_NAME.__file__))")

# Destination folder
DEST="./src/vault/$LIB_NAME"

# Copy the folder
echo "Copying from: $LIB_PATH"
echo "To: $DEST"
cp -r "$LIB_PATH" "$DEST"

echo "✅ Library '$LIB_NAME' copied to '$DEST'"

