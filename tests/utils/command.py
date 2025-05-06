#!/usr/bin/env python3
"""
Utility functions for running commands and interacting with canisters.
"""

from tests.utils.colors import print_ok, print_error
import os
import subprocess
import sys
import json

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


def run_command(command):
    """Run a shell command and return its output."""
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print_error(f"Error executing command: {command}")
        print_error(f"Error: {process.stderr}")
        return None
    return process.stdout.strip()


def run_command_expects_response_obj(command):
    """Run a shell command and return its output as a JSON object."""
    result = run_command(command)
    if not result:
        print_error(f"✗ Failed to run command `{command}`")
        return False

    result_json = json.loads(result)
    success = result_json.get("success", False)

    if not success:
        message = result_json.get("message", "Unknown error")
        print_error(f"✗ Failed to run command `{command}`: {message}")
        return False

    return result_json


def get_canister_id(canister_name):
    """Get the canister ID for the given canister name."""
    result = run_command(f"dfx canister id {canister_name}")
    if not result:
        raise Exception(f"Failed to get ID of canister {canister_name}")
    return result


def get_current_principal():
    """Get the principal ID of the current identity."""
    principal = run_command("dfx identity get-principal")
    if not principal:
        raise Exception("Failed to get principal")
    return principal


def deploy_ckbtc_ledger(initial_balance=1_000_000_000, transfer_fee=10):
    """
    Deploy the ckBTC ledger canister with specified parameters.

    Args:
        initial_balance: Initial token balance for the current principal
        transfer_fee: Fee for token transfers

    Returns:
        str: Canister ID of the deployed ledger, or None if deployment failed
    """
    print(f"Deploying ckbtc_ledger canister...")

    # Get current principal for controller and initial balance
    current_principal = get_current_principal()
    if not current_principal:
        return None

    # Fixed minting principal for test environment
    minting_principal = "aaaaa-aa"

    # Construct the deploy command with all parameters
    deploy_cmd = f"""dfx deploy --no-wallet ckbtc_ledger --argument="(variant {{ 
      Init = record {{ 
        minting_account = record {{ 
          owner = principal \\"{minting_principal}\\"; 
          subaccount = null 
        }}; 
        transfer_fee = {transfer_fee}; 
        token_symbol = \\"ckBTC\\"; 
        token_name = \\"ckBTC Test\\"; 
        decimals = opt 8; 
        metadata = vec {{}}; 
        initial_balances = vec {{ 
          record {{ 
            record {{ 
              owner = principal \\"{current_principal}\\"; 
              subaccount = null 
            }}; 
            {initial_balance} 
          }} 
        }}; 
        feature_flags = opt record {{ 
          icrc2 = true 
        }}; 
        archive_options = record {{ 
          num_blocks_to_archive = 1000; 
          trigger_threshold = 2000; 
          controller_id = principal \\"{current_principal}\\" 
        }} 
      }} 
    }})" """

    # Execute the deploy command
    run_command(deploy_cmd)

    # Get the ledger canister ID
    ledger_id = get_canister_id("ckbtc_ledger")
    if ledger_id:
        print_ok(f"✓ ckbtc_ledger canister deployed with ID: {ledger_id}")

    return ledger_id


def deploy_ckbtc_indexer(ledger_id=None, interval_seconds=1):
    """
    Deploy the ckBTC indexer canister with specified parameters.

    Args:
        ledger_id: Principal ID of the ckBTC ledger canister
        interval_seconds: Interval in seconds for retrieving blocks from ledger

    Returns:
        str: Canister ID of the deployed indexer, or None if deployment failed
    """
    print("Deploying ckbtc_indexer canister...")

    # If ledger_id not provided, try to get it
    if not ledger_id:
        ledger_id = get_canister_id("ckbtc_ledger")
        if not ledger_id:
            print_error("Cannot deploy indexer: ckbtc_ledger canister ID not found")
            return None

    # Construct the deploy command
    deploy_cmd = f"""dfx deploy --no-wallet ckbtc_indexer --argument="(opt variant {{ 
      Init = record {{ 
        ledger_id = principal \\"{ledger_id}\\"; 
        retrieve_blocks_from_ledger_interval_seconds = opt {interval_seconds} 
      }} 
    }})" """

    # Execute the deploy command
    run_command(deploy_cmd)

    # Get the indexer canister ID
    indexer_id = get_canister_id("ckbtc_indexer")
    if indexer_id:
        print_ok(f"ckbtc_indexer canister deployed with ID: {indexer_id}")

    return indexer_id


def update_transaction_history_until_no_more_transactions():
    loop_count = 0
    while loop_count < 20:
        loop_count += 1
        response = run_command("dfx canister call vault update_transaction_history --output json")
        response_json = json.loads(response)
        success = response_json.get("success", False)
        if not success:
            print_error("Failed to update transaction history")
            return False

        new_count = int(response_json.get("data")[0].get("TransactionSummary").get("new_count"))
        print(f"New count: {new_count}")
        if new_count == 0:
            return True
    
    raise Exception("Failed to update transaction history completely after max iterations")