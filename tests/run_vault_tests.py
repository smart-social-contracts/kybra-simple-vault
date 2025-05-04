#!/usr/bin/env python3
"""
Main test runner for the vault canister tests.
"""

import os
import sys

# Add the parent directory to the Python path to make imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from tests.test_cases.balance_tests import test_balance
from tests.test_cases.transaction_tests import (
    test_get_transactions,
    test_update_transactions,
)
from tests.test_cases.transfer_tests import (
    test_transfer_from_vault,
    test_transfer_to_vault,
)
from tests.utils.colors import GREEN, RED, RESET


def main():
    """Run the vault canister tests."""
    print(f"{GREEN}=== Starting Vault IC Tests ==={RESET}")

    # Transfer tokens to the vault
    transfer_to_success = test_transfer_to_vault(1000)

    # Transfer tokens from the vault
    transfer_success = test_transfer_from_vault(100)

    # Update transaction history
    update_success = test_update_transactions(2)

    # Check balance
    balance_success = test_balance(
        1000 - 100
    )  # balance of vault and user (900 and -100, respectively)

    # Get transaction history
    tx_success = test_get_transactions([100, 1000])

    # Print test summary
    print(f"\n{GREEN}=== Test Summary ==={RESET}")
    print(f"Token Transfer To: {'✓' if transfer_to_success else '✗'}")
    print(f"Token Transfer From: {'✓' if transfer_success else '✗'}")
    print(f"Transaction Update: {'✓' if update_success else '✗'}")
    print(f"Balance Check: {'✓' if balance_success else '✗'}")
    print(f"Transaction History: {'✓' if tx_success else '✗'}")

    # Check if all tests passed
    tests_passed = (
        transfer_to_success
        and transfer_success
        and update_success
        and balance_success
        and tx_success
    )

    if tests_passed:
        print(f"{GREEN}All tests passed!{RESET}")
        return 0
    else:
        print(f"{RED}Some tests failed!{RESET}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
