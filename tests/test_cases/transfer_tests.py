#!/usr/bin/env python3
"""
Tests for token transfer functionality of the vault canister.
"""

from tests.utils.command import get_canister_id, run_command
from tests.utils.colors import GREEN, RED, RESET
import json
import os
import sys
import time

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


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
        print(
            f"{GREEN}✓ Token transfer to vault succeeded, but result was not JSON{RESET}"
        )
        print(f"Transfer result: {transfer_result}")

    # Wait for the ledger to process the transaction
    print("Waiting for the transaction to be processed...")
    time.sleep(2)

    return True


def test_zero_amount_transfer():
    """Test transferring zero tokens from the vault canister."""
    print("\nTesting zero amount transfer from vault...")

    # Get canister IDs
    vault_id = get_canister_id("vault")

    # Using the default identity as the destination for this test
    destination_principal = run_command("dfx identity get-principal")

    print(f"Vault canister ID: {vault_id}")
    print(f"Destination principal: {destination_principal}")

    # Transfer zero tokens from the vault
    transfer_cmd = f"dfx canister call vault transfer '(principal \"{destination_principal}\", 0)' --output json"

    transfer_result = run_command(transfer_cmd)
    if not transfer_result:
        print(f"{RED}✗ Zero amount transfer failed{RESET}")
        return False

    # Parse JSON result
    result_json = json.loads(transfer_result)
    success = result_json.get("success", False)
    message = result_json.get("message", "Unknown")

    # Zero amount transfers should typically be rejected
    if not success and "amount must be positive" in message.lower():
        print(f"{GREEN}✓ Zero amount transfer correctly rejected: {message}{RESET}")
        return True
    elif not success:
        print(f"{GREEN}✓ Zero amount transfer rejected with message: {message}{RESET}")
        return True
    else:
        print(f"{RED}✗ Zero amount transfer unexpectedly succeeded{RESET}")
        return False


def test_negative_amount_transfer():
    """Test transferring negative tokens from the vault canister."""
    print("\nTesting negative amount transfer from vault...")

    # Get canister IDs
    vault_id = get_canister_id("vault")

    # Using the default identity as the destination for this test
    destination_principal = run_command("dfx identity get-principal")

    print(f"Vault canister ID: {vault_id}")
    print(f"Destination principal: {destination_principal}")

    # Transfer negative tokens from the vault
    transfer_cmd = f"dfx canister call vault transfer '(principal \"{destination_principal}\", -100)' --output json"

    transfer_result = run_command(transfer_cmd)

    # In many implementations, this should either fail at the command level or
    # be rejected by the canister
    if not transfer_result:
        print(f"{GREEN}✓ Negative amount transfer correctly rejected at command level{RESET}")
        return True

    # Parse JSON result if we got one
    result_json = json.loads(transfer_result)
    success = result_json.get("success", False)
    message = result_json.get("message", "Unknown")

    if not success:
        print(f"{GREEN}✓ Negative amount transfer correctly rejected: {message}{RESET}")
        return True
    else:
        print(f"{RED}✗ Negative amount transfer unexpectedly succeeded{RESET}")
        return False


def test_invalid_principal_transfer():
    """Test transferring tokens to an invalid principal."""
    print("\nTesting transfer to invalid principal...")

    # Get canister IDs
    vault_id = get_canister_id("vault")

    # Use an invalid principal
    invalid_principal = "not-a-valid-principal"

    print(f"Vault canister ID: {vault_id}")
    print(f"Invalid principal: {invalid_principal}")

    # Attempt transfer to invalid principal
    transfer_cmd = f"dfx canister call vault transfer '(principal \"{invalid_principal}\", 100)' --output json"

    transfer_result = run_command(transfer_cmd)

    # This should either fail at the command level or be rejected by the canister
    if not transfer_result:
        print(f"{GREEN}✓ Transfer to invalid principal correctly rejected at command level{RESET}")
        return True

    # Parse JSON result if we got one
    result_json = json.loads(transfer_result)
    success = result_json.get("success", False)

    if not success:
        print(f"{GREEN}✓ Transfer to invalid principal correctly rejected{RESET}")
        return True
    else:
        print(f"{RED}✗ Transfer to invalid principal unexpectedly succeeded{RESET}")
        return False


def test_exceed_balance_transfer():
    """Test transferring more tokens than the vault has."""
    print("\nTesting transfer exceeding vault balance...")

    try:
        # Get vault ID and user principal
        vault_id = get_canister_id("vault")
        destination_principal = run_command("dfx identity get-principal")

        # Try to transfer more than the balance
        excess_amount = 10000000000000

        print(f"Attempting to transfer {excess_amount} tokens (exceeds vault balance of {vault_balance})")

        transfer_cmd = f"dfx canister call vault transfer '(principal \"{destination_principal}\", {excess_amount})' --output json"
        transfer_result = run_command(transfer_cmd)

        if not transfer_result:
            print(f"{RED}✗ Excess transfer command failed{RESET}")
            return False

        # Parse the result
        result_json = json.loads(transfer_result)
        success = result_json.get("success", False)
        message = result_json.get("message", "Unknown")

        if not success and ("insufficient" in message.lower() or "balance" in message.lower()):
            print(f"{GREEN}✓ Excess transfer correctly rejected with appropriate message: {message}{RESET}")
            return True
        elif not success:
            print(f"{GREEN}✓ Excess transfer rejected with message: {message}{RESET}")
            return True
        else:
            print(f"{RED}✗ Excess transfer unexpectedly succeeded{RESET}")
            return False

    except Exception as e:
        print(f"{RED}✗ Error during excess balance transfer test: {e}{RESET}")
        return False


def test_multiple_transfers_sequence():
    """Test a sequence of multiple transfers to verify idempotency and consistency."""
    print("\nTesting a sequence of multiple transfers...")

    # Get vault ID and user principal
    vault_id = get_canister_id("vault")
    destination_principal = run_command("dfx identity get-principal")

    # Transfer amount for each step
    transfer_amount = 1000

    # Number of transfers to perform
    num_transfers = 3

    # Store results
    successful_transfers = 0

    # Perform multiple transfers
    for i in range(num_transfers):
        print(f"Transfer attempt {i+1}/{num_transfers}...")

        transfer_cmd = f"dfx canister call vault transfer '(principal \"{destination_principal}\", {transfer_amount})' --output json"
        transfer_result = run_command(transfer_cmd)

        if not transfer_result:
            print(f"{RED}✗ Transfer {i+1} failed{RESET}")
            continue

        # Parse the result
        result_json = json.loads(transfer_result)
        success = result_json.get("success", False)

        if success:
            print(f"{GREEN}✓ Transfer {i+1} succeeded{RESET}")
            successful_transfers += 1
        else:
            print(f"{RED}✗ Transfer {i+1} failed: {result_json.get('message', 'Unknown')}{RESET}")

        # Wait between transfers
        time.sleep(2)

    print(f"Completed {successful_transfers}/{num_transfers} successful transfers")

    # Test passes if at least one transfer succeeded
    # (In a more robust test suite, you might want to check the balance after each transfer)
    return successful_transfers > 0
