#!/usr/bin/env python3
"""
Main test runner for the vault canister tests.
"""

import os
import sys

# Add the parent directory to the Python path to make imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Now that we've added the parent directory to the path, we can import from the tests package
from tests.utils.colors import GREEN, RED, RESET
from tests.test_cases.transfer_tests import (
    test_transfer_from_vault,
    test_transfer_to_vault,
    test_zero_amount_transfer,
    test_negative_amount_transfer,
    test_invalid_principal_transfer,
    test_exceed_balance_transfer,
    test_multiple_transfers_sequence,
)
from tests.test_cases.transaction_tests import (
    test_get_transactions,
    test_update_transactions,
    test_get_transactions_nonexistent_user,
    test_transaction_ordering,
    test_transaction_validity,
    test_multiple_updates,
)
from tests.test_cases.balance_tests import (
    test_balance,
    test_nonexistent_user_balance,
    test_invalid_principal,
)


def main():
    """Run the vault canister tests."""
    print(f"{GREEN}=== Starting Vault IC Tests ==={RESET}")

    # Test results
    results = {}

    # Transfer tokens to the vault
    results["Transfer To Vault"] = test_transfer_to_vault(1000)

    # Test sequence of transfers
    results["Multiple Transfers"] = test_multiple_transfers_sequence()

    # Transfer tokens from the vault
    results["Transfer From Vault"] = test_transfer_from_vault(100)

    # Edge cases for transfers
    results["Zero Amount Transfer"] = test_zero_amount_transfer()
    results["Negative Amount Transfer"] = test_negative_amount_transfer()
    results["Invalid Principal Transfer"] = test_invalid_principal_transfer()
    results["Exceed Balance Transfer"] = test_exceed_balance_transfer()

    # Update transaction history
    results["Transaction Update"] = test_update_transactions(2)
    results["Multiple Updates"] = test_multiple_updates()

    # Check balances
    results["Regular User and Vault Balance"] = test_balance(900, 900)  # Expected 1000 - 100
    results["Non-existent User Balance"] = test_nonexistent_user_balance()
    results["Invalid Principal Balance"] = test_invalid_principal()

    # Check transaction history
    results["Transaction History"] = test_get_transactions([0, -100, 1000])
    results["Non-existent User Transactions"] = test_get_transactions_nonexistent_user()
    results["Transaction Ordering"] = test_transaction_ordering()
    results["Transaction Validity"] = test_transaction_validity()

    # Print test summary
    print(f"\n{GREEN}=== Test Summary ==={RESET}")
    for test_name, passed in results.items():
        print(f"{test_name}: {'✓' if passed else '✗'}")

    # Count passed tests
    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)

    print(f"\n{GREEN}Passed {passed_count} of {total_count} tests ({passed_count/total_count*100:.1f}%){RESET}")

    # Check if all tests passed
    if all(results.values()):
        print(f"{GREEN}All tests passed!{RESET}")
        return 0
    else:
        print(f"{RED}Some tests failed!{RESET}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
