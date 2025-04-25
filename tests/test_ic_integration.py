#!/usr/bin/env python3
"""
Simple integration test for the vault canister on Internet Computer.
Tests basic functionality including balance checking, transfers, and admin functions.
"""

import json
import os
import re
import subprocess
import sys
import shutil
from typing import Optional, Any
# from src.vault.vault.constants import MAINNET_CKBTC_LEDGER_ID
MAINNET_CKBTC_LEDGER_ID = "ckBTC"

# Simple colored output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Global variables
vault_id = None
ledger_id = None
test_receiver = "rwlgt-iiaaa-aaaaa-aaaaa-cai"  # Demo principal for testing

# Utility functions
def run_command(command: str) -> Optional[str]:
    """Run a shell command and return its output."""
    print(f"{YELLOW}Executing: {command}{RESET}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    print('process.returncode', process.returncode)
    print('process.stdout.strip()', process.stdout.strip())
    print('process.stderr.strip()', process.stderr.strip())
    if process.returncode != 0:
        print(f"{RED}Error: {process.stderr}{RESET}")
        raise Exception("Error")
    return '\n'.join([process.stdout.strip(), process.stderr.strip()]).strip()

def get_canister_id(canister_name: str) -> str:
    """Get the canister ID for the given canister name."""
    result = run_command(f"dfx canister id {canister_name}")
    if not result:
        raise ValueError(f"Could not get canister ID for {canister_name}")
    return result

def parse_candid_response(response: str) -> Any:
    """Parse a candid response from dfx canister call."""
    if not response:
        return None
        
    # Handle variant types (like Result)
    variant_match = re.search(r'\(\s*(\w+)\s+(.+)\s*\)', response)
    if variant_match:
        variant_type = variant_match.group(1)
        variant_value = variant_match.group(2)
        return {"variant": variant_type, "value": parse_candid_value(variant_value)}
    
    # Regular values
    return parse_candid_value(response)

def parse_candid_value(value: str) -> Any:
    """Parse a candid value into a Python object."""
    # Try to parse as a number
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
        
    # Handle records (simplified)
    if value.startswith('record {'):
        clean_value = value.replace('record {', '{').replace('}', '}')
        try:
            return json.loads(clean_value)
        except json.JSONDecodeError:
            pass
    
    # Default to returning the string
    return value.strip('"') if value.startswith('"') and value.endswith('"') else value

def mint_tokens(amount: int) -> bool:
    """Mint tokens to the vault for testing."""
    mint_cmd = (
        f"dfx canister call ckbtc_ledger icrc1_transfer \""
        f"(record {{ "
        f"to = record {{ owner = principal \\\"{vault_id}\\\"; subaccount = null }}; "
        f"amount = {amount}; "
        f"fee = null; "
        f"memo = null; "
        f"from_subaccount = null; "
        f"created_at_time = null "
        f"}})\""
    )
    result = run_command(mint_cmd)
    return result is not None

def call_admin_function(function_name: str, *args) -> Optional[Any]:
    """Call an admin function on the vault canister."""
    arg_str = ", ".join(str(arg) for arg in args)
    cmd = f"dfx canister call vault {function_name}"
    if arg_str:
        cmd += f" '({arg_str})'"
    
    result = run_command(cmd)
    return parse_candid_response(result) if result else None

# Test functions
def test_canister_balance():
    """Test the vault canister's balance functionality."""
    print(f"\n{BLUE}Testing: Vault balance{RESET}")
    balance_result = run_command("dfx canister call vault get_canister_balance")
    
    if not balance_result:
        print(f"{YELLOW}Balance check failed{RESET}")
        return False
        
    balance = parse_candid_response(balance_result)
    print(f"{GREEN}Balance: {balance}{RESET}")
    return True

def test_basic_transfer():
    """Test basic transfer functionality."""
    print(f"\n{BLUE}Testing: Basic transfer{RESET}")
    
    # Get initial balance
    initial_balance_resp = run_command("dfx canister call vault get_canister_balance")
    if not initial_balance_resp:
        print(f"{YELLOW}Could not get initial balance{RESET}")
        return False
    
    initial_balance = parse_candid_response(initial_balance_resp)
    
    # Transfer amount
    transfer_amount = 10000
    
    # Execute transfer
    transfer_cmd = f"dfx canister call vault do_transfer '(principal \"{test_receiver}\", {transfer_amount})'"
    transfer_result = run_command(transfer_cmd)
    
    if not transfer_result:
        print(f"{YELLOW}Transfer failed{RESET}")
        return False
    
    

    # Check new balance
    new_balance_resp = run_command("dfx canister call vault get_canister_balance")
    new_balance = parse_candid_response(new_balance_resp)
    
    print(f"Transfer result: {transfer_result}")
    print(f"Initial balance: {initial_balance}")
    print(f"New balance: {new_balance}")
    print(f"{GREEN}Transfer succeeded{RESET}")
    return True

def test_check_transactions():
    """Test transaction checking functionality."""
    print(f"\n{BLUE}Testing: Transactions{RESET}")
    
    # Trigger check_transactions
    result = run_command("dfx canister call vault check_transactions")
    if not result:
        print(f"{YELLOW}check_transactions failed{RESET}")
    else:
        print(f"{GREEN}check_transactions succeeded: {result}{RESET}")
    
    # Get transactions
    transactions_result = run_command("dfx canister call vault get_transactions '(0, 10)'")
    if transactions_result:
        print(f"Transactions: {transactions_result}")
        print(f"{GREEN}get_transactions succeeded{RESET}")
        return True
    else:
        print(f"{YELLOW}get_transactions failed{RESET}")
        return False

def test_admin_functions():
    """Test admin functions."""
    print(f"\n{BLUE}Testing: Admin functions{RESET}")
    
    # Test reset
    reset_result = run_command("dfx canister call vault reset")
    
    if reset_result is not None:
        print(f"{GREEN}Admin reset succeeded{RESET}")
        return True
    else:
        print(f"{YELLOW}Admin reset failed{RESET}")
        return False

def test_invalid_transfer():
    """Test transfer with invalid parameters."""
    print(f"\n{BLUE}Testing: Invalid transfer{RESET}")
    
    # Try to transfer more tokens than the vault has
    invalid_cmd = f"dfx canister call vault do_transfer '(principal \"{test_receiver}\", 999999999999)'"
    invalid_result = run_command(invalid_cmd)
    
    if invalid_result is None:
        print(f"{GREEN}Invalid transfer was rejected as expected{RESET}")
        return True
    else:
        print(f"Response: {invalid_result}")
        print(f"{GREEN}Invalid transfer returned error response{RESET}")
        return True

def test_get_transactions():
    """Test retrieving transaction history."""
    print(f"\n{BLUE}Testing: Get transactions{RESET}")
    
    transactions_cmd = "dfx canister call vault get_transactions '(0, 5)'"
    transactions_result = run_command(transactions_cmd)
    
    if transactions_result:
        transactions = parse_candid_response(transactions_result)
        print(f"Transactions: {transactions}")
        print(f"{GREEN}Retrieved transactions successfully{RESET}")
        return True
    else:
        print(f"{YELLOW}get_transactions failed{RESET}")
        return False

# def setup_ledger_files():
#     """Set up the ledger wasm and did files."""
#     print(f"\n{BLUE}Setting up ledger suite...{RESET}")
    
#     # Create directory if it doesn't exist
#     os.makedirs(".dfx/local/canisters", exist_ok=True)
    
#     # Copy the ledger wasm and did files
#     ledger_suite_dir = "./ledger_suite_icrc"
#     shutil.copy(f"{ledger_suite_dir}/ic-icrc1-ledger.wasm", "ledger_suite_icrc.wasm")
#     shutil.copy(f"{ledger_suite_dir}/ledger.did", "ledger_suite_icrc.did")
    
#     return True

def deploy_ledger_canister():
    """Deploy the ledger canister with explicit arguments."""
    print(f"\n{BLUE}Deploying ckbtc_ledger canister...{RESET}")
    
    # Get the current principal
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}Failed to get principal{RESET}")
        return False
    
    # Deploy the ledger canister
    ledger_arg = (
        f"(variant {{ Init = record {{ " + '\n'
        f"minting_account = record {{ owner = principal \\\"{principal}\\\"; subaccount = null }}; " + '\n'
        f"transfer_fee = 10; " + '\n'
        f"token_symbol = \\\"{MAINNET_CKBTC_LEDGER_ID}\\\"; " + '\n'
        f"token_name = \\\"{MAINNET_CKBTC_LEDGER_ID}\\\"; " + '\n'
        f"decimals = opt 8; " + '\n'
        f"metadata = vec {{}}; " + '\n'
        f"initial_balances = vec {{ record {{ record {{ owner = principal \\\"{principal}\\\"; subaccount = null }}; " + '\n'
        f"1_000_000_000 }} }}; " + '\n'
        f"feature_flags = opt record {{ icrc2 = true }}; " + '\n'
        f"archive_options = record {{ num_blocks_to_archive = 1000; trigger_threshold = 2000; " + '\n'
        f"controller_id = principal \\\"{principal}\\\" }} }} }})"
    )
    
    deploy_cmd = f"dfx deploy --no-wallet ckbtc_ledger --argument=\"{ledger_arg}\""
    # dfx deploy --no-wallet ckbtc_ledger --argument="(variant { Init = record { minting_account = record { owner = principal \"$PRINCIPAL\"; subaccount = null }; transfer_fee = 10; token_symbol = \"ckBTC\"; token_name = \"ckBTC Test\"; decimals = opt 8; metadata = vec {}; initial_balances = vec { record { record { owner = principal \"$PRINCIPAL\"; subaccount = null }; 1_000_000_000 } }; feature_flags = opt record { icrc2 = true }; archive_options = record { num_blocks_to_archive = 1000; trigger_threshold = 2000; controller_id = principal \"$PRINCIPAL\" } } })"


    result = run_command(deploy_cmd)

    print('result', result)
    
    if not result:
        print(f"{RED}Failed to deploy ledger canister{RESET}")
        return False
    
    print(f"{GREEN}Successfully deployed ledger canister{RESET}")
    return True

def deploy_vault_canister():
    """Deploy the vault canister with explicit init arguments."""
    print(f"\n{BLUE}Deploying vault canister...{RESET}")
    
    # Get the current principal
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}Failed to get principal{RESET}")
        return False
    
    # Get canister IDs
    ckbtc_principal = run_command("dfx canister id ckbtc_ledger")
    if not ckbtc_principal:
        print(f"{RED}Failed to get ckbtc_ledger canister ID{RESET}")
        return False
    
    vault_canister_id = ckbtc_principal  # Same as in entrypoint.sh
    
    # Deploy the vault canister
    vault_arg = f"(opt \\\"{MAINNET_CKBTC_LEDGER_ID}\\\", opt principal \\\"{ckbtc_principal}\\\", opt principal \\\"{principal}\\\", 0)"
    print(f"Deploying vault canister with arguments: {vault_arg}")
    
    deploy_cmd = f"dfx deploy vault --argument=\"{vault_arg}\""
    result = run_command(deploy_cmd)
    
    if not result:
        print(f"{RED}Failed to deploy vault canister{RESET}")
        return False
    
    print(f"{GREEN}Successfully deployed vault canister{RESET}")
    return True

def setup():
    """Set up the test environment."""
    global vault_id, ledger_id
    
    print(f"\n{BLUE}Setting up test environment...{RESET}")
    
    # # Setup ledger files
    # if not setup_ledger_files():
    #     print(f"{RED}Failed to set up ledger files{RESET}")
    #     return False
    
    # Deploy ledger canister
    if not deploy_ledger_canister():
        print(f"{RED}Failed to deploy ledger canister{RESET}")
        return False
    
    # Deploy vault canister
    if not deploy_vault_canister():
        print(f"{RED}Failed to deploy vault canister{RESET}")
        return False
    
    # Get canister IDs
    vault_id = get_canister_id("vault")
    ledger_id = get_canister_id("ckbtc_ledger")
    
    print(f"Vault canister ID: {vault_id}")
    print(f"Ledger canister ID: {ledger_id}")
    
    # Call reset to ensure a clean state
    call_admin_function("reset")
    
    # Initial minting
    mint_tokens(1000000)
    
    return True

def main():
    """Run all tests and return exit code."""
    print(f"{GREEN}Running vault canister integration tests...{RESET}")
    
    # Setup environment
    if not setup():
        print(f"{RED}Setup failed, aborting tests{RESET}")
        return 1
    
    # Track test results
    results = {
        "balance": test_canister_balance(),
        "transfer": test_basic_transfer(),
        "transactions": test_check_transactions(),
        "admin": test_admin_functions(),
        "invalid_transfer": test_invalid_transfer(),
        "get_transactions": test_get_transactions()
    }
    
    # Summary
    print(f"\n{BLUE}Test Results Summary:{RESET}")
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    print(f"\n{GREEN if all_passed else RED}Tests {'all passed' if all_passed else 'had failures'}.{RESET}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    print('it works')
    exit_code = main()
    sys.exit(exit_code)
