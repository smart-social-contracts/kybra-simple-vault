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
from tests.test_cases.deployment_tests import test_upgrade
from tests.test_cases.deployment_tests import (
    test_deploy_vault_with_params,
    test_deploy_vault_without_params,
    test_set_canisters,
)
from tests.test_cases.transaction_tests import test_get_transactions
from tests.test_cases.transaction_tests import (
    test_get_transactions_nonexistent_user,
    test_transaction_ordering,
    test_transaction_validity,
)
from tests.test_cases.transfer_tests import (
    test_exceed_balance_transfer,
    test_multiple_transfers_sequence,
    test_negative_amount_transfer,
    test_transfer_from_vault,
    test_transfer_to_vault,
    test_zero_amount_transfer,
)
from tests.utils.colors import print_error, print_ok
from tests.utils.command import create_test_identities
from tests.utils.command import execute_transactions
from tests.utils.command import get_canister_id
from tests.utils.command import (
    deploy_ckbtc_indexer,
    deploy_ckbtc_ledger,
    run_command,
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
        results["Transfer To Vault"] = test_transfer_to_vault(1000)

        # Transfer tokens from the vault
        results["Transfer From Vault"] = test_transfer_from_vault(100)

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
