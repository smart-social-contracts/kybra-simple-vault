#!/usr/bin/env python3
"""
Test runner specifically for test mode functionality.
"""

# isort: off
import traceback
import os
import sys

# Add the parent directory to the Python path to make imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# isort: on

from tests.test_cases.test_mode_tests import run_all_test_mode_tests
from tests.utils.colors import print_error, print_ok
from tests.utils.command import (
    deploy_ckbtc_indexer,
    deploy_ckbtc_ledger,
)


def main():
    """Run the test mode tests."""
    try:
        print("=== Starting Test Mode Tests ===")

        # Deploy ckBTC ledger and indexer for testing
        # Note: Test mode tests will mostly use mock behavior, but we still need
        # the infrastructure in place for complete testing
        deploy_ckbtc_ledger(
            initial_balance=1_000_000_000,  # Current principal gets 1B tokens
            transfer_fee=10,
        )
        deploy_ckbtc_indexer()

        # Run all test mode tests
        results = run_all_test_mode_tests()

        # Print test summary
        print("\n=== Test Mode Test Summary ===")
        for test_name, passed in results.items():
            if passed:
                print_ok(test_name)
            else:
                print_error(test_name)

        # Count passed tests
        passed_count = sum(1 for passed in results.values() if passed)
        total_count = len(results)

        print_ok(
            f"\nPassed {passed_count} of {total_count} test mode tests ({passed_count/total_count*100:.1f}%)"
        )

        # Check if all tests passed
        if all(results.values()):
            print_ok("All test mode tests passed!")
            return 0
        else:
            print_error("Some test mode tests failed!")
            return 1
    except Exception as e:
        print_error(f"Error running test mode tests: {e}\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
