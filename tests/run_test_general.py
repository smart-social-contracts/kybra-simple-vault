#!/usr/bin/env python3
"""
Main test runner for the vault canister tests.
"""


# isort: off
import traceback
import os
import sys

# Add the parent directory to the Python path to make imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# isort: on


from tests.test_cases.create_transaction_tests import run_all_tests as run_create_transaction_tests
from tests.test_cases.deployment_tests import (
    test_add_remove_admin,
    test_deploy_vault_without_params,
    test_set_canisters,
    test_upgrade,
)
from tests.test_cases.transaction_tests import (
    test_get_transactions_nonexistent_user,
    test_transaction_ordering,
    test_transaction_validity,
)
from tests.test_cases.transfer_tests import (
    test_exceed_balance_transfer,
    test_negative_amount_transfer,
    test_zero_amount_transfer,
    transfer_from_vault,
    transfer_to_vault,
)
from tests.utils.colors import print_error, print_ok
from tests.utils.command import (
    deploy_ckbtc_indexer,
    deploy_ckbtc_ledger,
    get_current_principal,
    update_transaction_history,
)


def main():
    """Run the vault canister tests."""
    try:
        print("=== Starting Vault IC Tests ===")

        deploy_ckbtc_ledger(
            initial_balance=1_000_000_000,  # Current principal gets 1B tokens
            transfer_fee=10,
        )
        deploy_ckbtc_indexer()

        results = {}

        # Deploy the vault canister
        results["Deploy Vault Without Params"] = test_deploy_vault_without_params()
        results["Set canisters"] = test_set_canisters()

        # Transfer tokens to the vault
        results["Transfer To Vault"] = transfer_to_vault(1000)

        # Transfer tokens from the vault
        results["Transfer From Vault"] = transfer_from_vault(
            get_current_principal(), 100
        )

        # Edge cases for transfers
        results["Zero Amount Transfer"] = test_zero_amount_transfer()
        results["Negative Amount Transfer"] = test_negative_amount_transfer()
        results["Exceed Balance Transfer"] = test_exceed_balance_transfer()

        # results["Non-existent User Balance"] = test_nonexistent_user_balance()

        # Check transaction history
        results["Non-existent User Transactions"] = (
            test_get_transactions_nonexistent_user()
        )

        update_transaction_history()

        # Check transaction ordering and validity
        results["Transaction Ordering"] = test_transaction_ordering()
        results["Transaction Validity"] = test_transaction_validity()

        # Test create_transaction_record functionality
        results["Create Transaction Record Tests"] = run_create_transaction_tests()

        # Test set canisters and ensure only the admin can do so
        if not test_set_canisters():
            return 1

        # Test add_admin and remove_admin functionality and admin controls
        if not test_add_remove_admin():
            return 1

        # Upgrade the vault canister
        results["Upgrade Vault"] = test_upgrade()

        # Print test summary
        print("\n=== Test Summary ===")
        for test_name, passed in results.items():
            if passed:
                print_ok(test_name)
            else:
                print_error(test_name)

        # Count passed tests
        passed_count = sum(1 for passed in results.values() if passed)
        total_count = len(results)

        print_ok(
            f"\nPassed {passed_count} of {total_count} tests ({passed_count/total_count*100:.1f}%)"
        )

        # Check if all tests passed
        if all(results.values()):
            print_ok("All tests passed!")
            return 0
        else:
            print_error("Some tests failed!")
            return 1
    except Exception as e:
        print_error(f"Error running tests: {e}\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
