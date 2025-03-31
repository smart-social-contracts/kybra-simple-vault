#!/bin/bash

# Exit on error
set -e

# Function to install and copy a library
install_and_copy_library() {
    local lib_name=$1
    
    echo "Installing and copying library: $lib_name"
    
    # Install the library
    pip install $lib_name
    
    # Use Python to find the path to the library
    local lib_path=$(python -c "import $lib_name; import os; print(os.path.dirname($lib_name.__file__))")
    
    # Destination folder
    local dest="./src/vault/$lib_name"
    
    # Copy the folder
    echo "Copying from: $lib_path"
    echo "To: $dest"
    cp -r "$lib_path" "$dest"
    
    echo "✅ Library '$lib_name' copied to '$dest'"
}

# Install libraries
install_and_copy_library "kybra_simple_db"
install_and_copy_library "kybra_simple_logging"
