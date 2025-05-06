#!/usr/bin/env python3
"""
Tests for deploying the vault canister with specific parameters.
"""

from tests.utils.command import get_canister_id, get_current_principal, run_command
from tests.utils.colors import GREEN, RED, RESET
from src.vault.vault.constants import CANISTER_PRINCIPALS, MAX_ITERATIONS, MAX_RESULTS
import json
import os
import subprocess
import sys
import traceback

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


def get_and_check_status(admin_principal, ledger_id, indexer_id, max_iterations, max_results):
    # run: dfx canister call vault status --output json
    # compare the result with the given params:

    try:

        status_cmd = "dfx canister call vault status --output json"
        status_result = run_command(status_cmd)

        print(f"Comparing status result with params {admin_principal, ledger_id, indexer_id, max_iterations, max_results} against: {status_result}")

        if not status_result:
            print(f"{RED}✗ Failed to check vault status{RESET}")
            return False

        status_json = json.loads(status_result)
        if not status_json.get("success", False):
            print(f"{RED}✗ Vault status check failed{RESET}")
            return False

        stats_data = status_json["data"][0]["Stats"]

        assert stats_data['app_data']['admin_principal'][0] == admin_principal
        assert stats_data['app_data']['max_iterations'] == str(max_iterations)
        assert stats_data['app_data']['max_results'] == str(max_results)

        tuples_to_check = [
            ("ckBTC indexer", indexer_id),
            ("ckBTC ledger", ledger_id)
        ]

        assert all(t in {(item["_id"], item["principal"]) for item in stats_data['canisters']} for t in tuples_to_check)

    except AssertionError as e:
        print(f"{RED}✗ Error while checking vault status: {e}\n{traceback.format_exc()}{RESET}")
        return False

    return True


def test_deploy_vault_with_params(max_iterations, max_results):
    """Test deploying the vault canister with specific initialization parameters."""
    print("\nTesting vault deployment with initialization parameters...")

    run_command("dfx canister delete vault --yes || true")

    # First, get the ledger and indexer canister IDs
    ledger_id = get_canister_id("ckbtc_ledger")
    indexer_id = get_canister_id("ckbtc_indexer")

    # Create deploy command with all parameters
    deploy_cmd = f"""dfx deploy vault --argument="(
      opt vec {{ 
        record {{ \\"ckBTC ledger\\"; principal \\"{ledger_id}\\" }};
        record {{ \\"ckBTC indexer\\"; principal \\"{indexer_id}\\" }}
      }},
      opt principal \\"{get_current_principal()}\\",
      opt {max_iterations},
      opt {max_results}
    )" """
    run_command(deploy_cmd)

    return get_and_check_status(get_current_principal(), ledger_id, indexer_id, max_iterations, max_results)


def test_deploy_vault_without_params():
    """Test deploying the vault canister without specifying initialization parameters."""
    print("\nTesting vault deployment without initialization parameters.")

    run_command("dfx canister delete vault --yes || true")

    # Default values
    ledger_id = CANISTER_PRINCIPALS['ckBTC']['ledger']
    indexer_id = CANISTER_PRINCIPALS['ckBTC']['indexer']
    max_iterations = MAX_ITERATIONS
    max_results = MAX_RESULTS

    print('Default values:\nledger_id: ', ledger_id, '\nindexer_id: ', indexer_id, '\nmax_iterations: ', max_iterations, '\nmax_results: ', max_results)

    # Deploy the vault without any arguments (relying on default values)
    deploy_cmd = "dfx deploy vault"

    run_command(deploy_cmd)

    return get_and_check_status(get_current_principal(), ledger_id, indexer_id, max_iterations, max_results)


def test_reinstall_vault():
    # TODO
    # - checks status, balances and transaction history
    # - checks update transactions and transfer
    pass


def test_set_canisters():
    """Test that only admin can set canisters in the vault."""
    print("\nTesting set_canisters functionality...")

    # Get canister IDs
    ledger_id = get_canister_id("ckbtc_ledger")
    indexer_id = get_canister_id("ckbtc_indexer")

    # Test setting canisters with admin identity
    print("Testing setting canisters as admin...")
    
    set_cmd = f"""dfx canister call vault set_canister '(\"ckBTC ledger\", \"{ledger_id}\")' --output json"""
    run_command_expects_response_obj(set_cmd)

    set_cmd = f"""dfx canister call vault set_canister '(\"ckBTC indexer\", \"{indexer_id}\")' --output json"""
    run_command_expects_response_obj(set_cmd)

    return get_and_check_status(get_current_principal(), ledger_id, indexer_id, MAX_ITERATIONS, MAX_RESULTS)


def test_set_admin():
    """Test that only admin can set a new admin in the vault."""
    print("\nTesting set_admin functionality...")

    # Get current user principal (current admin)
    current_admin = get_current_principal()
    if not current_admin:
        return False

    # We'll use the same principal as both current and new admin for testing
    # In a real scenario, you might want to use a different principal
    new_admin = current_admin

    # Test setting admin with admin identity
    print("Testing setting admin as current admin...")
    set_cmd = f'dfx canister call vault set_admin "(principal \\"{new_admin}\\")" --output json'

    try:
        result = run_command(set_cmd)
        if not result:
            print(f"{RED}✗ Failed to set admin{RESET}")
            return False

        result_json = json.loads(result)
        success = result_json.get("success", False)

        if not success:
            message = result_json.get("message", "Unknown error")
            print(f"{RED}✗ Failed to set admin: {message}{RESET}")
            return False

        print(f"{GREEN}✓ Successfully set admin{RESET}")

        # Verify admin was set by checking status
        status_cmd = "dfx canister call vault status --output json"
        status_result = run_command(status_cmd)

        if not status_result:
            print(f"{RED}✗ Failed to get vault status{RESET}")
            return False

        status_json = json.loads(status_result)
        if not status_json.get("success", False):
            print(f"{RED}✗ Vault status check failed{RESET}")
            return False

        # Extract admin from status
        try:
            status_data = status_json["data"][0]["Status"]
            admin = status_data.get("admin", "")

            if new_admin in admin:
                print(f"{GREEN}✓ Admin verified in vault status{RESET}")
            else:
                print(f"{RED}✗ Admin not set correctly in vault status{RESET}")
                return False

        except (KeyError, IndexError) as e:
            print(f"{RED}✗ Error extracting admin from status: {e}{RESET}")
            return False

        print(f"{GREEN}✓ set_admin functionality works correctly{RESET}")
        return True

    except Exception as e:
        print(f"{RED}✗ Error in set_admin test: {e}\n{traceback.format_exc()}{RESET}")
        return False


if __name__ == "__main__":
    test_deploy_vault_with_params()
    test_deploy_vault_without_params()
    test_reinstall_vault()
    test_set_canisters()
    test_set_admin()
