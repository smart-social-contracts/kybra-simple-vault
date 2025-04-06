#!/usr/bin/env python3
"""
Simplified IC environment test for the vault canister.
This script focuses only on testing the vault canister's balance and transfer functionality.
It interacts with the canister using dfx commands via subprocess.
"""

import subprocess
import sys
import time

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def run_command(command):
    """Run a shell command and return its output."""
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"{RED}Error executing command: {command}{RESET}")
        print(f"Error: {process.stderr}")
        return None
    return process.stdout.strip()

def get_canister_id(canister_name):
    """Get the canister ID for the given canister name."""
    result = run_command(f'dfx canister id {canister_name}')
    if not result:
        sys.exit(1)
    return result

def test_canister_deployment():
    """Test that the canisters are deployed and get their IDs."""
    print("Testing canister deployment...")
    vault_id = get_canister_id('vault')
    ledger_id = get_canister_id('ckbtc_ledger')
    print(f"Vault canister ID: {vault_id}")
    print(f"Ledger canister ID: {ledger_id}")
    return vault_id, ledger_id

def test_vault_balance():
    """Test the vault canister's balance functionality."""
    print("\nTesting vault balance functionality...")
    try:
        # Call the get_canister_balance method
        balance_result = run_command('dfx canister call vault get_canister_balance')
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

def test_mint_tokens(ledger_id, vault_id):
    """Mint some tokens to the vault for transfer testing."""
    print("\nMinting tokens to vault...")
    mint_cmd = f'dfx canister call ckbtc_ledger icrc1_transfer \'(record {{ to = record {{ owner = principal "{vault_id}"; subaccount = null }}; amount = 1000000; fee = null; memo = null; from_subaccount = null; created_at_time = null }})\''
    
    mint_result = run_command(mint_cmd)
    if mint_result:
        print(f"{GREEN}✓ Token minting succeeded{RESET}")
        print(f"Mint result: {mint_result}")
        return True
    else:
        print(f"{RED}✗ Token minting failed{RESET}")
        return False

def test_transfer():
    """Test the vault canister's transfer functionality."""
    print("\nTesting vault transfer functionality...")
    # Create a test receiver account
    test_receiver = "rwlgt-iiaaa-aaaaa-aaaaa-cai"  # Demo principal for testing
    
    try:
        # Call the do_transfer method with Principal
        transfer_result = run_command(f'dfx canister call vault do_transfer \'(principal "{test_receiver}", 100000)\'')
        if transfer_result:
            print(f"{GREEN}✓ Transfer succeeded{RESET}")
            print(f"Transfer result: {transfer_result}")
            return True
        else:
            print(f"{RED}✗ Transfer failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error during transfer: {e}{RESET}")
        return False

def main():
    """Run simplified tests for the vault canister focusing on balance and transfer."""
    print(f"{GREEN}=== Starting Simplified Vault Canister Tests ==={RESET}")
    
    # Test canister deployment
    vault_id, ledger_id = test_canister_deployment()
    
    # Test vault balance before transfers
    initial_balance_success = test_vault_balance()
    
    # Mint tokens to the vault
    mint_success = test_mint_tokens(ledger_id, vault_id)
    
    # Give the ledger canister time to process the mint
    if mint_success:
        print("Waiting for mint to be processed...")
        time.sleep(2)
    
    # Test transfer
    transfer_success = test_transfer()
    
    # Test vault balance after transfers
    final_balance_success = test_vault_balance()
    
    # Summary
    print(f"\n{GREEN}=== Test Summary ==={RESET}")
    print(f"Initial Balance Check: {'✓' if initial_balance_success else '✗'}")
    print(f"Token Minting: {'✓' if mint_success else '✗'}")
    print(f"Transfer: {'✓' if transfer_success else '✗'}")
    print(f"Final Balance Check: {'✓' if final_balance_success else '✗'}")
    
    tests_passed = initial_balance_success and mint_success and transfer_success and final_balance_success
    
    if tests_passed:
        print(f"{GREEN}All tests passed!{RESET}")
        return 0
    else:
        print(f"{RED}Some tests failed!{RESET}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)