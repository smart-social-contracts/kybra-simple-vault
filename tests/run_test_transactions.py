#!/usr/bin/env python3
"""
Transaction test runner for the vault canister.

This module tests the transaction capabilities of the vault canister, focusing on:
- Deposit transactions into the vault
- Withdrawal transactions from the vault
- Balance verification after transactions
- Transaction history synchronization
- User-to-user transfers via the vault

It deploys all necessary canisters (ckBTC ledger, indexer, vault) and sets up
test identities before running the transaction sequence.
"""

import sys
import traceback

# Add the parent directory to the Python path to make imports work
sys.path.insert(0, sys.path[0] + "/..")

from tests.test_cases.deployment_tests import test_deploy_vault_with_params
from tests.utils.colors import print_error, print_ok
from tests.utils.command import (
    create_test_identities,
    deploy_ckbtc_indexer,
    deploy_ckbtc_ledger,
    execute_transactions,
)

# Test configuration constants
INITIAL_TRANSFER_AMOUNT = 101  # Starting amount for transfers
MAX_RESULTS = 2  # Max results parameter for vault deployment
MAX_ITERATION_COUNT = 2  # Max iteration count parameter for vault deployment

# Initial balances for test identities
IDENTITY_BALANCES = {
    "alice": 500_000_000,
    "bob": 300_000_000,
    "charlie": 100_000_000,
}


def main():
    """
    Run the vault transaction tests.

    This function:
    1. Creates test identities (alice, bob, charlie)
    2. Deploys the ckBTC ledger with initial balances
    3. Deploys the ckBTC indexer
    4. Deploys the vault canister with test parameters
    5. Executes a sequence of test transactions
    6. Verifies results and reports success/failure

    Returns:
        int: 0 for success, 1 for failure
    """
    try:
        print("=== Starting Vault IC Tests ===")

        # Create test identities
        print("\nCreating test identities...")
        identities = create_test_identities(["alice", "bob", "charlie"])
        print(f"Created identities: {', '.join(identities.keys())}")

        # Deploy ck canisters with initial balances for identities
        print("\nDeploying ckBTC ledger with initial balances...")
        deploy_ckbtc_ledger(
            initial_balance=1_000_000_000,  # Current principal gets 1B tokens
            transfer_fee=10,
            identities=identities,
            identity_balances=IDENTITY_BALANCES,
        )
        deploy_ckbtc_indexer()

        # Test results
        results = {}

        # Deploy the vault canister
        results["Deploy Vault With Params"] = test_deploy_vault_with_params(
            max_results=MAX_RESULTS, max_iteration_count=MAX_ITERATION_COUNT
        )

        # Define a more comprehensive transaction sequence
        print("\nExecuting transaction sequence...")
        transactions = [
            # Basic deposits
            ["alice", "vault"],  # Alice deposits to vault (amount: 101)
            ["update_history", None],  # Update transaction history
            ["check_balance", "alice"],  # Verify Alice's balance = 101
            ["bob", "vault"],  # Bob deposits to vault (amount: 102)
            ["update_history", None],  # Update transaction history
            ["check_balance", "bob"],  # Verify Bob's balance = 102
            # Additional transaction: Charlie deposits
            ["charlie", "vault"],  # Charlie deposits to vault (amount: 103)
            ["update_history", None],  # Update transaction history
            ["check_balance", "charlie"],  # Verify Charlie's balance = 103
            # Withdrawal transaction
            ["vault", "alice"],  # Withdraw to Alice (amount: 104)
            ["update_history", None],  # Update transaction history
            ["check_balance", "alice"],  # Verify updated Alice balance = 101 - 104 = -3
            # Advanced: vault makes multiple transfers
            ["vault", "bob"],  # Withdraw to Bob (amount: 105)
            [
                "bob",
                "charlie",
            ],  # Out-of-vault transfer from Bob to Charlie (amount: 106)
            ["update_history", None],  # Update transaction history
            # Final balance verification
            ["check_balance", "alice"],  # Verify Alice's final balance
            ["check_balance", "bob"],  # Verify Bob's final balance
            ["check_balance", "charlie"],  # Verify Charlie's final balance
        ]

        # Execute transactions and track expected balances
        print("Executing transactions...")
        success, expected_balances = execute_transactions(
            transactions,
            identities=identities,
            start_amount=INITIAL_TRANSFER_AMOUNT,
            initial_balances=IDENTITY_BALANCES.copy(),
        )

        results["Transaction Sequence"] = success

        print("\nExpected Balances After Transactions:")
        for account, balance in expected_balances.items():
            print(f"  {account}: {balance}")

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
