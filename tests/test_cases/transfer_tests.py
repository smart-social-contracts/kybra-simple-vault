#!/usr/bin/env python3
"""
Tests for token transfer functionality of the vault canister.
"""

import json
import os
import sys
import time
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
        vault_id = get_canister_id("vault")
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


def transfer_to_vault(from_principal, amount):
    """Helper function to transfer tokens to the vault from a principal."""
    try:
        vault_id = get_canister_id("vault")
        ledger_id = get_canister_id("ckbtc_ledger")

        print(f"Transferring {amount} tokens to vault from {from_principal}")

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


def test_transfer_from_vault(amount=100):
    """Test transferring tokens from the vault canister to another account."""
    print(f"\nTesting token transfer from vault with amount {amount}...")

    # Get the destination principal (current identity)
    destination_principal = get_current_principal()
    if not destination_principal:
        return False

    # Execute the transfer
    _, success = transfer_from_vault(destination_principal, amount)

    # Wait for the transaction to be processed
    if success:
        print("Waiting for the transaction to be processed...")
        time.sleep(2)

    return success


def test_transfer_to_vault(amount=100):
    """Test transferring tokens to the vault canister."""
    print(f"\nTesting token transfer to vault with amount {amount}...")

    # Get the source principal (current identity)
    source_principal = get_current_principal()
    if not source_principal:
        return False

    # Execute the transfer
    _, success = transfer_to_vault(source_principal, amount)

    # Wait for the transaction to be processed
    if success:
        print("Waiting for the transaction to be processed...")
        time.sleep(2)

    return success


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


# def test_invalid_principal_transfer():
#     """Test transferring tokens to an invalid principal."""
#     print("\nTesting transfer to invalid principal...")

#     # Use an invalid principal format that will be caught by the Base32 check
#     invalid_principal = (
#         "aaaaa-aaaa-aaaa-aaaa-aaaaa"  # Valid Base32 but likely invalid principal
#     )

#     # Try to transfer to invalid principal
#     result_json, success = transfer_from_vault(invalid_principal, 100)

#     # Invalid principal transfers should be rejected
#     if not success:
#         if result_json is None:
#             print(
#                 f"{GREEN}✓ Transfer to invalid principal correctly rejected at command level{RESET}"
#             )
#         else:
#             message = result_json.get("message", "")
#             print(
#                 f"{GREEN}✓ Transfer to invalid principal correctly rejected: {message}{RESET}"
#             )
#         return True
#     else:
#         print(f"{RED}✗ Transfer to invalid principal unexpectedly succeeded{RESET}")
#         return False


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


def test_multiple_transfers_sequence(transfer_amounts):
    """Test a sequence of multiple transfers to verify consistency."""
    print("\nTesting a sequence of multiple transfers...")

    # Get destination principal
    destination_principal = get_current_principal()
    if not destination_principal:
        return False

    # Perform multiple transfers
    successful_transfers = 0
    num_transfers = len(transfer_amounts)

    for i in range(num_transfers):
        print(f"Transfer attempt {i+1}/{num_transfers}...")

        _, success = transfer_from_vault(destination_principal, transfer_amounts[i])

        if success:
            successful_transfers += 1
            # Wait between transfers
            time.sleep(2)

    print(f"Completed {successful_transfers}/{num_transfers} successful transfers")

    # Test passes if at least one transfer succeeded
    return successful_transfers > 0
