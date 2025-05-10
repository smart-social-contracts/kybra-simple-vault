#!/usr/bin/env python3
"""
Tests for token transfer functionality of the vault canister.
"""

import json
import os
import sys
import traceback

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import GREEN, RED, RESET
from tests.utils.command import get_canister_id, get_current_principal, run_command


def transfer_from_vault(to_principal, amount):
    """Helper function to transfer tokens from vault to a principal."""
    try:
        print(f"Transferring {amount} tokens from vault to {to_principal}")

        transfer_cmd = f"dfx canister call vault transfer '(principal \"{to_principal}\", {amount})' --output json"
        transfer_result = run_command(transfer_cmd)

        if not transfer_result:
            print(f"{RED}✗ Transfer command failed{RESET}")
            return None, False

        result_json = json.loads(transfer_result)
        success = result_json.get("success", False)
        message = result_json.get("message", "Unknown")

        if success:
            print(f"{GREEN}✓ Transfer of {amount} tokens succeeded{RESET}")
        else:
            print(f"{RED}✗ Transfer failed: {message}{RESET}")

        return result_json, success
    except Exception as e:
        print(f"{RED}✗ Error executing transfer: {e}\n{traceback.format_exc()}{RESET}")
        return None, False


def transfer_to_vault(amount):
    """Helper function to transfer tokens to the vault from a principal."""
    try:

        from_principal = get_current_principal()
        print(f"Transferring {amount} tokens to vault from {from_principal}")

        vault_id = get_canister_id("vault")

        transfer_cmd = f"dfx canister call ckbtc_ledger icrc1_transfer '(record {{ to = record {{ owner = principal \"{vault_id}\"; subaccount = null }}; amount = {amount}; fee = null; memo = null; from_subaccount = null; created_at_time = null }})' --output json"
        transfer_result = run_command(transfer_cmd)

        if not transfer_result:
            print(f"{RED}✗ Token transfer to vault failed{RESET}")
            return None, False

        try:
            result_json = json.loads(transfer_result)
            print(f"{GREEN}✓ Token transfer to vault succeeded{RESET}")
            return result_json, True
        except json.JSONDecodeError:
            print(
                f"{GREEN}✓ Token transfer to vault succeeded, but result was not JSON{RESET}"
            )
            return transfer_result, True
    except Exception as e:
        print(
            f"{RED}✗ Error transferring to vault: {e}\n{traceback.format_exc()}{RESET}"
        )
        return None, False


def test_zero_amount_transfer():
    """Test transferring zero tokens from the vault canister."""
    print("\nTesting zero amount transfer from vault...")

    # Get the destination principal
    destination_principal = get_current_principal()
    if not destination_principal:
        return False

    # Try to transfer zero tokens
    result_json, success = transfer_from_vault(destination_principal, 0)

    # Zero amount transfers should be rejected
    if not success:
        message = result_json.get("message", "") if result_json else ""
        if "amount must be positive" in message.lower():
            print(f"{GREEN}✓ Zero amount transfer correctly rejected: {message}{RESET}")
        else:
            print(
                f"{GREEN}✓ Zero amount transfer rejected with message: {message}{RESET}"
            )
        return True
    else:
        print(f"{RED}✗ Zero amount transfer unexpectedly succeeded{RESET}")
        return False


def test_negative_amount_transfer():
    """Test transferring negative tokens from the vault canister."""
    print("\nTesting negative amount transfer from vault...")

    # Get the destination principal
    destination_principal = get_current_principal()
    if not destination_principal:
        return False

    # Try to transfer negative tokens
    result_json, success = transfer_from_vault(destination_principal, -100)

    # Negative amount transfers should be rejected
    if not success:
        if result_json is None:
            print(
                f"{GREEN}✓ Negative amount transfer correctly rejected at command level{RESET}"
            )
        else:
            message = result_json.get("message", "")
            print(
                f"{GREEN}✓ Negative amount transfer correctly rejected: {message}{RESET}"
            )
        return True
    else:
        print(f"{RED}✗ Negative amount transfer unexpectedly succeeded{RESET}")
        return False


def test_exceed_balance_transfer():
    """Test transferring more tokens than the vault has."""
    print("\nTesting transfer exceeding vault balance...")

    # Get the destination principal
    destination_principal = get_current_principal()
    if not destination_principal:
        return False

    # Try to transfer an excessive amount
    very_large_amount = 10000000000000  # Intentionally very large
    result_json, success = transfer_from_vault(destination_principal, very_large_amount)

    # Excessive transfers should be rejected
    if not success:
        message = result_json.get("message", "") if result_json else ""
        if "insufficient" in message.lower() or "balance" in message.lower():
            print(
                f"{GREEN}✓ Excess transfer correctly rejected with appropriate message: {message}{RESET}"
            )
        else:
            print(f"{GREEN}✓ Excess transfer rejected with message: {message}{RESET}")
        return True
    else:
        print(f"{RED}✗ Excess transfer unexpectedly succeeded{RESET}")
        return False
