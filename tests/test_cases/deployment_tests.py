#!/usr/bin/env python3
"""
Tests for deploying the vault canister with specific parameters.
"""

from tests.utils.command import get_canister_id, get_current_principal, run_command, run_command_expects_response_obj
from tests.utils.colors import GREEN, RED, RESET, print_ok, print_error
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
            print_error("Failed to check vault status")
            return False

        status_json = json.loads(status_result)
        if not status_json.get("success", False):
            print_error("Vault status check failed")
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
        print_error(f"Error while checking vault status: {e}\n{traceback.format_exc()}")
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


def test_upgrade():
    """Test upgrading the vault canister while preserving state."""
    print("\nTesting vault canister upgrade...")
    
    # Step 1: Store current state before upgrade
    
    # Get current principal for testing
    current_principal = get_current_principal()
    
    # Get current status
    status_cmd = "dfx canister call vault status --output json"
    pre_status = run_command(status_cmd)
    if not pre_status:
        print_error("Failed to get vault status before upgrade")
        return False
    
    # Get current balance
    balance_cmd = f"dfx canister call vault get_balance '(\"{current_principal}\")' --output json"
    pre_balance = run_command_expects_response_obj(balance_cmd)
    if not pre_balance:
        print_error("Failed to get balance before upgrade")
        return False
    
    # Get existing transactions
    transactions_cmd = f"dfx canister call vault get_transactions '(\"{current_principal}\")' --output json"
    pre_transactions = run_command_expects_response_obj(transactions_cmd)
    if not pre_transactions:
        print_error("Failed to get transactions before upgrade")
        return False
    
    pre_tx_count = len(pre_transactions.get("data", []))
    print(f"Pre-upgrade transaction count: {pre_tx_count}")
    
    # Step 2: Perform the upgrade
    print_ok("Upgrading vault canister...")
    upgrade_cmd = "dfx deploy vault --mode upgrade"
    upgrade_result = run_command(upgrade_cmd)
    if not upgrade_result:
        print_error("Failed to upgrade vault canister")
        return False
    
    # Step 3: Verify state is preserved
    
    # Check status after upgrade
    post_status = run_command(status_cmd)
    if not post_status:
        print_error("Failed to get vault status after upgrade")
        return False
    
    # Check balance is preserved
    post_balance = run_command_expects_response_obj(balance_cmd)
    if not post_balance:
        print_error("Failed to get balance after upgrade")
        return False
    
    # Compare balance amounts
    pre_balance_amount = pre_balance.get("data", [{}])[0].get("amount", "0")
    post_balance_amount = post_balance.get("data", [{}])[0].get("amount", "0")
    if pre_balance_amount != post_balance_amount:
        print_error(f"Balance not preserved after upgrade: before={pre_balance_amount}, after={post_balance_amount}")
        return False
    
    # Check transactions are preserved
    post_transactions = run_command_expects_response_obj(transactions_cmd)
    if not post_transactions:
        print_error("Failed to get transactions after upgrade")
        return False
    
    post_tx_count = len(post_transactions.get("data", []))
    if post_tx_count < pre_tx_count:
        print_error(f"Transactions not preserved after upgrade: before={pre_tx_count}, after={post_tx_count}")
        return False
    
    # Test that transfer functionality still works
    print_ok("Testing transfer functionality after upgrade...")
    post_transfer_cmd = f"dfx canister call vault transfer '(principal \"{current_principal}\", 25)' --output json"
    post_transfer_result = run_command_expects_response_obj(post_transfer_cmd)
    if not post_transfer_result:
        print_error("Failed to perform transfer after upgrade")
        return False
    
    # Update transaction history
    update_tx_cmd = "dfx canister call vault update_transaction_history --output json"
    run_command_expects_response_obj(update_tx_cmd)
    
    # Verify new transaction was added
    final_transactions = run_command_expects_response_obj(transactions_cmd)
    if not final_transactions:
        print_error("Failed to get final transactions")
        return False
    
    final_tx_count = len(final_transactions.get("data", []))
    if final_tx_count <= post_tx_count:
        print_error("New transaction was not recorded after upgrade")
        return False
    
    print_ok("Vault canister upgraded successfully with state preserved")
    return True


def test_set_canisters():
    """Test that only admin can set canisters in the vault."""
    print("\nTesting set_canisters functionality...")

    # Get canister IDs
    ledger_id = get_canister_id("ckbtc_ledger")
    indexer_id = get_canister_id("ckbtc_indexer")

    # Test setting canisters with admin identity
    print("Testing setting canisters as admin...")

    set_cmd = f"""dfx canister call vault set_canister '(\"ckBTC ledger\", principal \"{ledger_id}\")' --output json"""
    run_command_expects_response_obj(set_cmd)

    set_cmd = f"""dfx canister call vault set_canister '(\"ckBTC indexer\", principal \"{indexer_id}\")' --output json"""
    run_command_expects_response_obj(set_cmd)

    return get_and_check_status(get_current_principal(), ledger_id, indexer_id, MAX_ITERATIONS, MAX_RESULTS)


if __name__ == "__main__":
    test_deploy_vault_with_params(MAX_ITERATIONS, MAX_RESULTS)
    test_deploy_vault_without_params()
    test_upgrade()
    test_set_canisters()
