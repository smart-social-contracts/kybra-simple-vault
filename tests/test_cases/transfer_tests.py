#!/usr/bin/env python3
"""
Tests for token transfer functionality of the vault canister.
"""

import json
import os
import sys
import time

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import GREEN, RED, RESET
from tests.utils.command import get_canister_id, run_command


def test_transfer_from_vault(amount=100000):
    """Transfer tokens from the vault canister to another account for testing."""
    print(f"\nTesting token transfer from vault with amount {amount}...")

    # Get canister IDs``
    vault_id = get_canister_id("vault")

    # Using the default identity as the destination for this test
    # In a real scenario, you might want to use a different principal
    destination_principal = run_command("dfx identity get-principal")

    print(f"Vault canister ID: {vault_id}")
    print(f"Destination principal: {destination_principal}")

    # Transfer tokens from the vault
    transfer_cmd = f"dfx canister call vault transfer '(principal \"{destination_principal}\", {amount})' --output json"

    transfer_result = run_command(transfer_cmd)
    if not transfer_result:
        print(f"{RED}✗ Token transfer failed{RESET}")
        return False

    # Parse JSON result
    result_json = json.loads(transfer_result)
    success = result_json.get("success", False)
    message = result_json.get("message", "Unknown")
    
    if not success:
        print(f"{RED}✗ Token transfer failed: {message}{RESET}")
        return False
        
    print(f"{GREEN}✓ Token transfer succeeded{RESET}")
    print(f"Transfer result: {result_json}")

    # Wait for the transaction to be processed
    print("Waiting for the transaction to be processed...")
    time.sleep(2)

    return True


def test_transfer_to_vault(amount=50000):
    """Transfer tokens to the vault canister for testing."""
    print(f"\nTesting token transfer to vault with amount {amount}...")

    # Get canister IDs
    vault_id = get_canister_id("vault")
    ledger_id = get_canister_id("ckbtc_ledger")

    # Using the default identity as the source for this test
    source_principal = run_command("dfx identity get-principal")

    print(f"Vault canister ID: {vault_id}")
    print(f"Ledger canister ID: {ledger_id}")
    print(f"Source principal: {source_principal}")

    # Transfer tokens to the vault
    transfer_cmd = f"dfx canister call ckbtc_ledger icrc1_transfer '(record {{ to = record {{ owner = principal \"{vault_id}\"; subaccount = null }}; amount = {amount}; fee = null; memo = null; from_subaccount = null; created_at_time = null }})' --output json"

    transfer_result = run_command(transfer_cmd)
    if not transfer_result:
        print(f"{RED}✗ Token transfer to vault failed{RESET}")
        return False
    
    # Parse JSON result
    try:
        result_json = json.loads(transfer_result)
        print(f"{GREEN}✓ Token transfer to vault succeeded{RESET}")
        print(f"Transfer result: {result_json}")
    except json.JSONDecodeError:
        print(f"{GREEN}✓ Token transfer to vault succeeded, but result was not JSON{RESET}")
        print(f"Transfer result: {transfer_result}")

    # Wait for the ledger to process the transaction
    print("Waiting for the transaction to be processed...")
    time.sleep(2)

    return True
