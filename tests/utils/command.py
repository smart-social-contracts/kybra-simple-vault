#!/usr/bin/env python3
"""
Utility functions for running commands and interacting with canisters.
"""

import subprocess
import sys
from tests.utils.colors import GREEN, RED, RESET


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
