#!/usr/bin/env python3
"""
Simple test script for the vault canister with the mock indexer.
This script tests basic functionality of the vault including:
- Token deposits
- Balance checking
- Transaction history
"""

import subprocess
import sys
import time
import json

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


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


def test_mint_to_vault(amount=1000000):
    """Mint tokens directly to the vault canister for testing."""
    print(f"\nTesting token minting to vault with amount {amount}...")

    # Get canister IDs
    vault_id = get_canister_id("vault")
    ledger_id = get_canister_id("ckbtc_ledger")

    print(f"Vault canister ID: {vault_id}")
    print(f"Ledger canister ID: {ledger_id}")

    # Mint tokens to the vault
    mint_cmd = f"dfx canister call ckbtc_ledger icrc1_transfer '(record {{ to = record {{ owner = principal \"{vault_id}\"; subaccount = null }}; amount = {amount}; fee = null; memo = null; from_subaccount = null; created_at_time = null }})'"

    mint_result = run_command(mint_cmd)
    if not mint_result:
        print(f"{RED}✗ Token minting failed{RESET}")
        return False

    print(f"{GREEN}✓ Token minting succeeded{RESET}")
    print(f"Mint result: {mint_result}")

    # Wait for the ledger to process the transaction
    print("Waiting for the transaction to be processed...")
    time.sleep(2)

    return True


def test_transfer_from_vault(amount=100000):
    """Transfer tokens from the vault canister to another account for testing."""
    print(f"\nTesting token transfer from vault with amount {amount}...")

    # Get canister IDs
    vault_id = get_canister_id("vault")

    # Using the default identity as the destination for this test
    # In a real scenario, you might want to use a different principal
    destination_principal = run_command("dfx identity get-principal")

    print(f"Vault canister ID: {vault_id}")
    print(f"Destination principal: {destination_principal}")

    # Transfer tokens from the vault
    transfer_cmd = f"dfx canister call vault transfer '(principal \"{destination_principal}\", {amount})'"

    transfer_result = run_command(transfer_cmd)
    if not transfer_result:
        print(f"{RED}✗ Token transfer failed{RESET}")
        return False

    print(f"{GREEN}✓ Token transfer succeeded{RESET}")
    print(f"Transfer result: {transfer_result}")

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
    transfer_cmd = f"dfx canister call ckbtc_ledger icrc1_transfer '(record {{ to = record {{ owner = principal \"{vault_id}\"; subaccount = null }}; amount = {amount}; fee = null; memo = null; from_subaccount = null; created_at_time = null }})'"

    transfer_result = run_command(transfer_cmd)
    if not transfer_result:
        print(f"{RED}✗ Token transfer to vault failed{RESET}")
        return False

    print(f"{GREEN}✓ Token transfer to vault succeeded{RESET}")
    print(f"Transfer result: {transfer_result}")

    # Wait for the ledger to process the transaction
    print("Waiting for the transaction to be processed...")
    time.sleep(2)

    return True


def test_balance(expected_vault_balance=None, expected_user_balance=None):
    """Test checking the vault canister's balance."""
    print("\nTesting vault balance functionality...")

    # Get the principal of the current identity
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False

    try:
        # Call the get_balance method for the user
        balance_result = run_command(f"dfx canister call vault get_balance '(\"{principal}\")'")

        if balance_result:
            print(f"{GREEN}✓ User balance check succeeded{RESET}")
            print(f"User balance result: {balance_result}")
            
            # Verify expected user balance if provided
            if expected_user_balance is not None:
                # Extract the balance value from the result
                # Example: "(100 : nat)" -> extract "100"
                user_balance = int(balance_result.strip("()").split(":")[0].strip())
                if user_balance == expected_user_balance:
                    print(f"{GREEN}✓ User balance matches expected value: {expected_user_balance}{RESET}")
                else:
                    print(f"{RED}✗ User balance {user_balance} does not match expected value: {expected_user_balance}{RESET}")
                    return False
            
            # Get the vault canister ID
            vault_id = get_canister_id("vault")
            
            # Check the vault's balance
            vault_balance_result = run_command(f"dfx canister call vault get_balance '(\"{vault_id}\")'")
            
            if vault_balance_result:
                print(f"{GREEN}✓ Vault balance check succeeded{RESET}")
                print(f"Vault balance result: {vault_balance_result}")
                
                # Verify expected vault balance if provided
                if expected_vault_balance is not None:
                    # Extract the balance value from the result
                    vault_balance = int(vault_balance_result.strip("()").split(":")[0].strip().replace("_", ""))
                    if vault_balance == expected_vault_balance:
                        print(f"{GREEN}✓ Vault balance matches expected value: {expected_vault_balance}{RESET}")
                    else:
                        print(f"{RED}✗ Vault balance {vault_balance} does not match expected value: {expected_vault_balance}{RESET}")
                        return False
            
            return True
        else:
            print(f"{RED}✗ Balance check failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error checking balance: {e}{RESET}")
        return False


def test_update_transactions(expected_count=None):
    """Test updating transaction history in the vault."""
    print("\nTesting transaction history update...")

    # Get the principal of the current identity
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False

    try:
        # Update transaction history
        update_result = run_command(f"dfx canister call vault update_transaction_history")

        if update_result:
            print(f"{GREEN}✓ Transaction history update succeeded{RESET}")
            print(f"Update result: {update_result}")
            
            # Verify the expected count if provided
            if expected_count is not None:
                # Try to extract the count from the update result if it's returned
                print(f"Expected transaction count: {expected_count}")
                # This is just a placeholder check
                print(f"{GREEN}✓ Transaction count verification skipped{RESET}")
            
            return True
        else:
            print(f"{RED}✗ Transaction history update failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error updating transaction history: {e}{RESET}")
        return False


def test_get_transactions(expected_amounts=None):
    """Test retrieving transaction history from the vault."""
    print("\nTesting transaction history retrieval...")

    # Get the principal of the current identity
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False

    try:
        # Get transaction history
        tx_result = run_command(f"dfx canister call vault get_transactions '(\"{principal}\")'")

        if tx_result:
            print(f"{GREEN}✓ Transaction history retrieval succeeded{RESET}")
            print(f"Transaction result: {tx_result}")
            
            # Verify transaction amounts if expected_amounts is provided
            if expected_amounts is not None and isinstance(expected_amounts, list):
                print(f"Verifying transaction amounts: {expected_amounts}")
                
                # This is a basic check - you might need to adapt it based on your transaction format
                for amount in expected_amounts:
                    # Check if the amount appears in the transaction result
                    if f"amount = {amount}" in tx_result or f"amount = {amount}_000" in tx_result:
                        print(f"{GREEN}✓ Found transaction with amount {amount}{RESET}")
                    else:
                        print(f"{RED}✗ Could not find transaction with amount {amount}{RESET}")
                        return False
                
                print(f"{GREEN}✓ All expected transaction amounts were found{RESET}")
            
            return True
        else:
            print(f"{RED}✗ Transaction history retrieval failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error retrieving transaction history: {e}{RESET}")
        return False


def main():
    """Run the vault canister tests."""
    print(f"{GREEN}=== Starting Vault IC Tests ==={RESET}")

    # Mint tokens to the vault
    mint_success = test_mint_to_vault(1100)

    # Transfer tokens to the vault
    transfer_to_success = test_transfer_to_vault(1200)

    # Transfer tokens from the vault
    transfer_success = test_transfer_from_vault(1300)

    # Update transaction history
    update_success = test_update_transactions(3)

    # Check balance
    balance_success = test_balance(1100 + 1200 - 1300, -100)  # balance of vault and user (1000 and -100, respectively)

    # Get transaction history
    tx_success = test_get_transactions([1100, 1200, 1300])

    # Print test summary
    print(f"\n{GREEN}=== Test Summary ==={RESET}")
    print(f"Token Minting: {'✓' if mint_success else '✗'}")
    print(f"Token Transfer To: {'✓' if transfer_to_success else '✗'}")
    print(f"Token Transfer From: {'✓' if transfer_success else '✗'}")
    print(f"Transaction Update: {'✓' if update_success else '✗'}")
    print(f"Balance Check: {'✓' if balance_success else '✗'}")
    print(f"Transaction History: {'✓' if tx_success else '✗'}")

    # Check if all tests passed
    tests_passed = mint_success and transfer_to_success and transfer_success and update_success and balance_success and tx_success

    if tests_passed:
        print(f"{GREEN}All tests passed!{RESET}")
        return 0
    else:
        print(f"{RED}Some tests failed!{RESET}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    time.sleep(999999)
    sys.exit(exit_code)
