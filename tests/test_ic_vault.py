
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


def test_mint_to_vault():
    """Mint tokens directly to the vault canister for testing."""
    print("\nTesting token minting to vault...")
    
    # Get canister IDs
    vault_id = get_canister_id("vault")
    ledger_id = get_canister_id("ckbtc_ledger")
    
    print(f"Vault canister ID: {vault_id}")
    print(f"Ledger canister ID: {ledger_id}")
    
    # Mint 1,000,000 tokens to the vault (10^6)
    mint_amount = 1000000
    mint_cmd = f"dfx canister call ckbtc_ledger icrc1_transfer '(record {{ to = record {{ owner = principal \"{vault_id}\"; subaccount = null }}; amount = {mint_amount}; fee = null; memo = null; from_subaccount = null; created_at_time = null }})'"
    
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


def test_balance():
    """Test checking the vault canister's balance."""
    print("\nTesting vault balance functionality...")
    
    # Get the principal of the current identity
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False
    
    try:
        # Call the get_balance method
        balance_result = run_command(f"dfx canister call vault get_balance '(\"{principal}\")'")
        
        if balance_result:
            print(f"{GREEN}✓ Balance check succeeded{RESET}")
            print(f"Balance result: {balance_result}")
            return True
        else:
            print(f"{RED}✗ Balance check failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error checking balance: {e}{RESET}")
        return False


def test_update_transactions():
    """Test updating transaction history in the vault."""
    print("\nTesting transaction history update...")
    
    # Get the principal of the current identity
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False
    
    try:
        # Update transaction history
        update_result = run_command(f"dfx canister call vault update_transaction_history '(\"{principal}\")'")
        
        if update_result:
            print(f"{GREEN}✓ Transaction history update succeeded{RESET}")
            print(f"Update result: {update_result}")
            return True
        else:
            print(f"{RED}✗ Transaction history update failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error updating transaction history: {e}{RESET}")
        return False


def test_get_transactions():
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
    mint_success = test_mint_to_vault()
    
    # Update transaction history
    update_success = test_update_transactions()
    
    # Check balance
    balance_success = test_balance()
    
    # Get transaction history
    tx_success = test_get_transactions()
    
    # Print test summary
    print(f"\n{GREEN}=== Test Summary ==={RESET}")
    print(f"Token Minting: {'✓' if mint_success else '✗'}")
    print(f"Transaction Update: {'✓' if update_success else '✗'}")
    print(f"Balance Check: {'✓' if balance_success else '✗'}")
    print(f"Transaction History: {'✓' if tx_success else '✗'}")
    
    # Check if all tests passed
    tests_passed = mint_success and update_success and balance_success and tx_success
    
    if tests_passed:
        print(f"{GREEN}All tests passed!{RESET}")
        return 0
    else:
        print(f"{RED}Some tests failed!{RESET}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)