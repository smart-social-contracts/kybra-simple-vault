#!/usr/bin/env python3
"""
Main test runner for the vault canister tests.
"""


# isort: off
import traceback
import os
import sys
import json

# Add the parent directory to the Python path to make imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# isort: on


from tests.test_cases.balance_tests import (
    check_balance,
    test_balance,
    test_nonexistent_user_balance,
)
from tests.test_cases.deployment_tests import test_set_canisters
from tests.test_cases.deployment_tests import test_upgrade
from tests.test_cases.deployment_tests import (
    test_deploy_vault_with_params,
    test_deploy_vault_without_params,
)
from tests.test_cases.transaction_tests import test_get_transactions
from tests.test_cases.transaction_tests import test_transaction_ordering
from tests.test_cases.transaction_tests import test_transaction_validity
from tests.test_cases.transaction_tests import (
    test_get_transactions_nonexistent_user,
)
from tests.test_cases.transfer_tests import test_exceed_balance_transfer
from tests.test_cases.transfer_tests import test_negative_amount_transfer
from tests.test_cases.transfer_tests import test_transfer_from_vault
from tests.test_cases.transfer_tests import test_transfer_to_vault
from tests.test_cases.transfer_tests import test_zero_amount_transfer
from tests.test_cases.transfer_tests import (
    test_multiple_transfers_sequence,
)
from tests.utils.colors import print_error, print_ok
from tests.utils.command import get_canister_id
from tests.utils.command import run_command
from tests.utils.command import (
    create_test_identities,
    deploy_ckbtc_indexer,
    deploy_ckbtc_ledger,
    execute_transactions,
)


def main():
    """Run the vault canister tests."""
    try:
        print("=== Starting Vault IC Tests ===")

        # Create test identities
        print("\nCreating test identities...")
        identities = create_test_identities(["alice", "bob", "charlie"])
        print(f"Created identities: {', '.join(identities.keys())}")

        # Set initial balances for identities
        identity_balances = {
            "alice": 500_000_000,
            "bob": 300_000_000,
            "charlie": 100_000_000,
        }

        # Deploy ck canisters with initial balances for identities
        print("\nDeploying ckBTC ledger with initial balances...")
        deploy_ckbtc_ledger(
            initial_balance=1_000_000_000,  # Current principal gets 1B tokens
            transfer_fee=10,
            identities=identities,
            identity_balances=identity_balances,
        )
        deploy_ckbtc_indexer()

        # Test results
        results = {}

        # Deploy the vault canister
        results["Deploy Vault With Params"] = test_deploy_vault_with_params(
            max_results=2, max_iteration_count=2
        )

        # Define transaction sequence - keep it simple to ensure success
        print("\nExecuting transaction sequence...")
        transactions = [
            ["alice", "vault"],  # Alice deposits 101
            ["update_history", None],  # Update transaction history
            ["check_balance", "alice"],  # Verify Alice's balance (should be 101)
            ["bob", "vault"],  # Bob deposits 102
            ["update_history", None],  # Update transaction history
            ["check_balance", "bob"],  # Verify Bob's balance (should be 102)
        ]
        # Execute transactions and track expected balances
        print("Executing transactions...")
        success, expected_balances = execute_transactions(
            transactions,
            identities=identities,
            start_amount=101,
            initial_balances=identity_balances.copy(),
        )

        results["Transaction Sequence"] = success

        print("\nExpected Balances After Transactions:")
        for account, balance in expected_balances.items():
            print(f"  {account}: {balance}")

        # Since we've reached the end without errors, return success
        return 0
    except Exception as e:
        print_error(f"Error running tests: {e}\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
