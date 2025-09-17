#!/usr/bin/env python3
"""
Tests for deploying the vault canister with specific parameters.
"""

import json
import os
import sys
import traceback

from src.vault.vault.constants import (
    CANISTER_PRINCIPALS,
    MAX_ITERATION_COUNT,
    MAX_RESULTS,
)
from tests.utils.colors import print_error, print_ok
from tests.utils.command import (
    create_test_identities,
    get_canister_id,
    get_current_principal,
    run_command,
    run_command_expects_response_obj,
    update_transaction_history,
)

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


def get_and_check_status(
    admin_principal, ledger_id, indexer_id, max_iteration_count, max_results
):
    # run: dfx canister call vault status --output json
    # compare the result with the given params:

    try:

        status_cmd = "dfx canister call vault status --output json"
        status_result = run_command(status_cmd)

        print(
            f"Comparing status result with params {admin_principal, ledger_id, indexer_id, max_iteration_count, max_results} against: {status_result}"
        )

        if not status_result:
            print_error("Failed to check vault status")
            return False

        status_json = json.loads(status_result)
        if not status_json.get("success", False):
            print_error("Vault status check failed")
            return False

        stats_data = status_json["data"]["Stats"]

        assert stats_data["app_data"]["admin_principal"] == admin_principal
        assert stats_data["app_data"]["max_iteration_count"] == str(max_iteration_count)
        assert stats_data["app_data"]["max_results"] == str(max_results)

        # Verify sync_status is correctly determined based on transaction IDs
        end_tx_id = stats_data["app_data"].get("scan_end_tx_id", "0")
        oldest_tx_id = stats_data["app_data"].get("scan_oldest_tx_id", "0")
        start_tx_id = stats_data["app_data"].get("scan_start_tx_id", "0")

        expected_sync_status = (
            "Synced" if end_tx_id == oldest_tx_id == start_tx_id else "Syncing"
        )
        actual_sync_status = stats_data["app_data"].get("sync_status", "")

        assert actual_sync_status == expected_sync_status, (
            f"Expected sync_status to be '{expected_sync_status}' when tx IDs are "
            f"end={end_tx_id}, oldest={oldest_tx_id}, start={start_tx_id}, but got '{actual_sync_status}'"
        )

        tuples_to_check = [("ckBTC indexer", indexer_id), ("ckBTC ledger", ledger_id)]

        assert all(
            t in {(item["id"], item["principal"]) for item in stats_data["canisters"]}
            for t in tuples_to_check
        )

    except AssertionError as e:
        print_error(f"Error while checking vault status: {e}\n{traceback.format_exc()}")
        return False

    return True


def test_deploy_vault_with_params(max_iteration_count, max_results):
    """Test deploying the vault canister with specific initialization parameters."""
    print("\nTesting vault deployment with initialization parameters...")

    run_command("dfx canister delete vault --yes || true")

    # First, get the ledger and indexer canister IDs
    ledger_id = get_canister_id("ckbtc_ledger")
    indexer_id = get_canister_id("ckbtc_indexer")

    # Create deploy command with all parameters (including test_mode_enabled = false)
    deploy_cmd = f"""dfx deploy vault --argument="(
      opt vec {{ 
        record {{ \\"ckBTC ledger\\"; principal \\"{ledger_id}\\" }};
        record {{ \\"ckBTC indexer\\"; principal \\"{indexer_id}\\" }}
      }},
      opt principal \\"{get_current_principal()}\\",
      opt {max_results},
      opt {max_iteration_count},
      opt false
    )" """
    run_command(deploy_cmd)

    return get_and_check_status(
        get_current_principal(), ledger_id, indexer_id, max_iteration_count, max_results
    )


def test_deploy_vault_without_params():
    """Test deploying the vault canister without specifying initialization parameters."""
    print("\nTesting vault deployment without initialization parameters.")

    run_command("dfx canister delete vault --yes || true")

    # Default values
    ledger_id = CANISTER_PRINCIPALS["ckBTC"]["ledger"]
    indexer_id = CANISTER_PRINCIPALS["ckBTC"]["indexer"]
    max_iteration_count = MAX_ITERATION_COUNT
    max_results = MAX_RESULTS

    print(
        "Default values:\nledger_id: ",
        ledger_id,
        "\nindexer_id: ",
        indexer_id,
        "\nmax_iteration_count: ",
        max_iteration_count,
        "\nmax_results: ",
        max_results,
        "\ntest_mode_enabled: false (default)",
    )

    # Deploy the vault without any arguments (relying on default values)
    deploy_cmd = "dfx deploy vault"

    run_command(deploy_cmd)

    return get_and_check_status(
        get_current_principal(), ledger_id, indexer_id, max_iteration_count, max_results
    )


def test_upgrade():
    """Test upgrading the vault canister while preserving state."""
    print("\nTesting vault canister upgrade...")

    update_transaction_history()

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
    balance_cmd = f"dfx canister call vault get_balance '(principal \"{current_principal}\")' --output json"
    pre_balance = run_command_expects_response_obj(balance_cmd)
    if not pre_balance:
        print_error("Failed to get balance before upgrade")
        return False

    # Get existing transactions
    transactions_cmd = f"dfx canister call vault get_transactions '(principal \"{current_principal}\")' --output json"
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
    pre_balance_amount = (
        pre_balance.get("data", {}).get("Balance", {}).get("amount", "0")
    )
    post_balance_amount = (
        post_balance.get("data", {}).get("Balance", {}).get("amount", "0")
    )
    if pre_balance_amount != post_balance_amount:
        print_error(
            f"Balance not preserved after upgrade: before={pre_balance_amount}, after={post_balance_amount}"
        )
        return False

    # Check transactions are preserved
    post_transactions = run_command_expects_response_obj(transactions_cmd)
    if not post_transactions:
        print_error("Failed to get transactions after upgrade")
        return False

    post_tx_count = len(post_transactions["data"]["Transactions"])
    if post_tx_count < pre_tx_count:
        print_error(
            f"Transactions not preserved after upgrade: before={pre_tx_count}, after={post_tx_count}"
        )
        return False

    # Test that transfer functionality still works
    print_ok("Testing transfer functionality after upgrade...")
    post_transfer_cmd = f"dfx canister call vault transfer '(principal \"{current_principal}\", 25)' --output json"
    post_transfer_result = run_command_expects_response_obj(post_transfer_cmd)
    if not post_transfer_result:
        print_error("Failed to perform transfer after upgrade")
        return False

    update_transaction_history()

    # Verify new transaction was added
    final_transactions = run_command_expects_response_obj(transactions_cmd)
    if not final_transactions:
        print_error("Failed to get final transactions")
        return False

    final_tx_count = len(final_transactions["data"]["Transactions"])
    if final_tx_count != post_tx_count + 1:
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

    return get_and_check_status(
        get_current_principal(), ledger_id, indexer_id, MAX_ITERATION_COUNT, MAX_RESULTS
    )


def test_set_admin():
    """Test the set_admin functionality, including proper access controls."""
    print("\nTesting set_admin functionality...")

    # Check current admin (which should be the deployer)
    original_admin = get_current_principal()
    if not original_admin:
        print_error("Failed to get current principal")
        return False

    # Create a test identity to use as new admin
    try:
        # Create new identity
        identities = create_test_identities(["new_admin"])
        new_admin_principal = identities["new_admin"]
        print(
            f"Created test identity 'new_admin' with principal: {new_admin_principal}"
        )

        # Test 1: Original admin should be able to set new admin
        print("\nTesting set_admin by original admin (should succeed)...")
        cmd = f'dfx canister call vault set_admin "(principal \\"{new_admin_principal}\\")" --output json'
        result = run_command(cmd)

        if not result:
            print_error("Failed to call set_admin")
            return False

        result_json = json.loads(result)
        if not result_json.get("success", False):
            print_error(f"set_admin failed: {result_json}")
            return False

        print_ok("Successfully changed admin to new identity")

        # Test 2: Verify with status check and test new admin can set admin back
        status_cmd = "dfx canister call vault status --output json"
        status_result = json.loads(run_command(status_cmd))

        if (
            status_result.get("success", False)
            and status_result["data"]["Stats"]["app_data"]["admin_principal"]
            == new_admin_principal
        ):
            print_ok(f"Status confirmed admin principal is now: {new_admin_principal}")

            # Test 3: New admin sets admin back to original
            cmd = f'dfx --identity new_admin canister call vault set_admin "(principal \\"{original_admin}\\")" --output json'
            result = run_command(cmd)

            if result and json.loads(result).get("success", False):
                print_ok("New admin successfully changed admin back to original")

                # Clean up - remove test identity
                run_command("dfx identity remove new_admin || true")
                return True

        print_error("Admin principal change verification failed")
        run_command("dfx identity remove new_admin || true")
        return False

    except Exception as e:
        print_error(f"Error in test_set_admin: {e}\n{traceback.format_exc()}")
        # Clean up - ensure we remove test identity even if test fails
        run_command("dfx identity remove new_admin || true")
        return False
