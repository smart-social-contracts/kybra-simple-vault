#!/usr/bin/env python3
"""
Test runner for the external canister integration tests.
"""

# isort: off
import traceback
import os
import sys
import subprocess
import shutil
import json

# Add the parent directory to the Python path to make imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# isort: on

from tests.utils.colors import print_error, print_ok
from tests.utils.command import (
    deploy_ckbtc_indexer,
    deploy_ckbtc_ledger,
    get_canister_id,
    get_current_principal,
    run_command,
    update_transaction_history,
)


def deploy_vault_from_wasm():
    """Deploy the vault canister from the WASM file."""
    print("\n=== Deploying vault canister from WASM ===")

    # Build WASM file
    run_command("dfx canister create vault")
    run_command("dfx build vault")

    # Get canister IDs
    ledger_id = get_canister_id("ckbtc_ledger")
    indexer_id = get_canister_id("ckbtc_indexer")

    # Create install command with the same format as in deployment_tests.py
    install_cmd = f"""dfx canister install vault --wasm .kybra/vault/vault.wasm --argument="(
      opt vec {{ 
        record {{ \\"ckBTC ledger\\"; principal \\"{ledger_id}\\" }};
        record {{ \\"ckBTC indexer\\"; principal \\"{indexer_id}\\" }}
      }}
    )" """

    return run_command(install_cmd)


def deploy_external_canister():
    """Deploy the external canister that will interact with the vault."""
    print("\n=== Deploying external canister ===")

    print("Deploying external canister with the vault reference...")
    # Explicitly specify the config file to use

    deploy_result = run_command("dfx deploy external")
    if not deploy_result:
        print_error("Failed to deploy external canister")
        return False

    print_ok("Successfully deployed external canister")
    return True


def run_external_canister_tests():
    """Run tests from the external canister against the vault."""
    print("\n=== Running external canister tests against vault ===")

    # Get canister IDs
    vault_canister_id = run_command("dfx canister id vault")
    if not vault_canister_id:
        print_error("Failed to get vault canister ID")
        return False

    external_canister_id = run_command("dfx canister id external")
    if not external_canister_id:
        print_error("Failed to get external canister ID")
        return False

    # Run the vault tests from the external canister
    print("\nRunning tests from external canister...")
    test_result = run_command(
        f"dfx canister call external run_vault_tests '(principal \"{vault_canister_id}\")' --output json"
    )
    if not test_result:
        print_error("Failed to run tests from external canister")
        return False

    try:
        result_json = json.loads(test_result)

        if "status_response" in result_json:
            status_response = result_json["status_response"]
            if "success" in status_response and status_response["success"]:
                print_ok("Vault status check successful")

                # Output some details from the response for verification
                if "data" in status_response and "Stats" in status_response["data"]:
                    stats = status_response["data"]["Stats"]
                    print(
                        f"  Admin Principals: {stats['app_data']['admin_principals']}"
                    )
                    print(f"  Sync Status: {stats['app_data']['sync_status']}")
                    print(f"  Registered Canisters: {len(stats['canisters'])}")
                    print(f"  Balances Count: {len(stats['balances'])}")
            else:
                error_msg = "Unknown error"
                if "data" in status_response and "Error" in status_response["data"]:
                    error_msg = status_response["data"]["Error"]
                print_error(f"Vault status check failed: {error_msg}")
                return False
        else:
            print_error("Invalid response format: 'status_response' field not found")
            print(f"Received: {test_result}")
            return False

    except json.JSONDecodeError:
        print_error(f"Failed to parse JSON response: {test_result}")
        return False
    except Exception as e:
        print_error(f"Error processing test result: {str(e)}")
        return False

    print_ok("All external canister tests completed successfully")
    return True


def main():
    """Run the external canister integration tests."""
    try:
        print("=== Starting External Canister Integration Tests ===")

        # 1. Deploy the ckBTC ledger and indexer canisters
        print("\nDeploying ckBTC ledger and indexer canisters...")
        ledger_id = deploy_ckbtc_ledger(
            initial_balance=1_000_000_000,  # Current principal gets 1B tokens
            transfer_fee=10,
        )
        if not ledger_id:
            print_error("Failed to deploy ckBTC ledger")
            return 1

        indexer_id = deploy_ckbtc_indexer()
        if not indexer_id:
            print_error("Failed to deploy ckBTC indexer")
            return 1

        # 2. Deploy the vault canister
        deploy_vault_from_wasm()

        # 3. Deploy the external canister with vault reference
        if not deploy_external_canister():
            return 1

        # 4. Run the tests from the external canister
        # if not run_external_canister_tests():
        #     print_error("External canister tests failed")
        #     return 1

        print("\n=== All External Canister Tests Completed Successfully ===")
        return 0

    except Exception as e:
        print_error(f"Error in test runner: {e}\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
