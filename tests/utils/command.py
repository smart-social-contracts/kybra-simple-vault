#!/usr/bin/env python3
"""
Utility functions for running commands and interacting with canisters.
"""

import os
import subprocess
import sys

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import RED, RESET


def run_command(command):
    """Run a shell command and return its output."""
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"{RED}Error executing command: {command}{RESET}")
        print(f"Error: {process.stderr}")
        return None
    return process.stdout.strip()


def get_canister_id(canister_name):
    """Get the canister ID for the given canister name."""
    result = run_command(f"dfx canister id {canister_name}")
    if not result:
        sys.exit(1)
    return result


def get_current_principal():
    """Get the principal ID of the current identity."""
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return None
    return principal
