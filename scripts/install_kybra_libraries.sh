#!/bin/bash

# Exit on error
set -e

# Function to download and extract a library
download_and_extract_library() {
    local lib_name=$1
    
    echo "Downloading and extracting library: $lib_name"
    
    # Create temporary directory for download and extraction
    local temp_dir=$(mktemp -d)
    echo "Created temporary directory: $temp_dir"
    
    # Download the library wheel
    pip download --no-deps --dest "$temp_dir" $lib_name
    
    # Find the downloaded wheel file
    local wheel_file=$(find "$temp_dir" -name "*.whl" | head -n 1)
    
    if [ -z "$wheel_file" ]; then
        echo "Error: Could not find downloaded wheel for $lib_name"
        rm -rf "$temp_dir"
        exit 1
    fi
    
    echo "Downloaded wheel: $wheel_file"
    
    # Create extraction directory
    local extract_dir="$temp_dir/extract"
    mkdir -p "$extract_dir"
    
    # Extract the wheel (it's just a zip file)
    unzip -q "$wheel_file" -d "$extract_dir"
    
    # Find the package directory inside the extracted content
    local package_dir=$(find "$extract_dir" -type d -name "$lib_name" | head -n 1)
    
    if [ -z "$package_dir" ]; then
        echo "Error: Could not find package directory for $lib_name in extracted content"
        rm -rf "$temp_dir"
        exit 1
    fi
    
    # Destination folder
    local dest="./src/vault/$lib_name"
    
    # Delete the destination folder if it exists
    if [ -d "$dest" ]; then
        echo "Removing existing directory: $dest"
        rm -rf "$dest"
    fi
    
    # Copy the folder
    echo "Copying from: $package_dir"
    echo "To: $dest"
    cp -r "$package_dir" "$dest"
    
    # Clean up temporary directory
    rm -rf "$temp_dir"
    
    echo "✅ Library '$lib_name' copied to '$dest'"
}

# Download and extract libraries
download_and_extract_library "kybra_simple_db"
download_and_extract_library "kybra_simple_logging"
