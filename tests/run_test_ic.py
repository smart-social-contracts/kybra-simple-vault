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


from tests.utils.colors import print_ok, print_error
from tests.test_cases.deployment_tests import (
    test_deploy_vault_with_params,
    test_deploy_vault_without_params,
    test_set_canisters,
    test_upgrade
)
from tests.test_cases.transfer_tests import (
    test_exceed_balance_transfer,
    test_multiple_transfers_sequence,
    test_negative_amount_transfer,
    test_transfer_from_vault,
    test_transfer_to_vault,
    test_zero_amount_transfer,
)
from tests.test_cases.transaction_tests import (
    test_update_transactions_batches,
    test_get_transactions,
    test_get_transactions_nonexistent_user,
    test_transaction_ordering,
    test_transaction_validity,
)
from tests.test_cases.balance_tests import (
    test_balance,
    test_nonexistent_user_balance,
    check_balance
)
from tests.utils.command import (
    deploy_ckbtc_ledger,
    deploy_ckbtc_indexer,
    create_test_identities,
    execute_transactions,
    get_canister_id,
    run_command
)


def main():
    try:
        """Run the vault canister tests."""
        print("=== Starting Vault IC Tests ===")

        # Create test identities
        print("\nCreating test identities...")
        identities = create_test_identities(['alice', 'bob', 'charlie'])
        print(f"Created identities: {', '.join(identities.keys())}")
        
        # Set initial balances for identities
        identity_balances = {
            'alice': 500_000_000,
            'bob': 300_000_000,
            'charlie': 100_000_000
        }
        
        # Deploy ck canisters with initial balances for identities
        print("\nDeploying ckBTC ledger with initial balances...")
        deploy_ckbtc_ledger(
            initial_balance=1_000_000_000,  # Current principal gets 1B tokens
            transfer_fee=10,
            identities=identities,
            identity_balances=identity_balances
        )
        deploy_ckbtc_indexer()

        # Test results
        results = {}

        # Deploy the vault canister
        results["Deploy Vault With Params"] = test_deploy_vault_with_params(max_results=2, max_iteration_count=2)
        
        # Define transaction sequence
        print("\nExecuting transaction sequence...")
        transactions = [
            # Transfers to vault
            ['alice', 'vault'],      # Alice sends to vault
            ['bob', 'vault'],        # Bob sends to vault
            ['charlie', 'vault'],    # Charlie sends to vault
            
            # Transfers from vault
            ['vault', 'alice'],      # Vault sends to Alice
            ['vault', 'bob'],        # Vault sends to Bob
            
            # Update transaction history
            ['update_history', ''],
            
            # More transactions
            ['alice', 'vault'],      # Alice sends more to vault
            ['vault', 'charlie']     # Vault sends to Charlie
        ]
        
        # Execute transactions with auto-incrementing amounts (start at 101)
        success, expected_balances = execute_transactions(
            transaction_pairs=transactions,
            identities=identities,
            start_amount=101
        )
        
        results["Transaction Sequence"] = success
        
        print("\nExpected Balances After Transactions:")
        for account, balance in expected_balances.items():
            if account != 'vault':  # Skip vault in this loop
                print(f"  {account}: {balance}")
        
        # Verify balances
        print("\nVerifying balances...")
        balance_verification_success = True
        
        # Check all balances (vault + identities)
        to_check = {'vault': get_canister_id("vault")}
        to_check.update({name: pid for name, pid in identities.items() if name in expected_balances})
        
        for name, principal_id in to_check.items():
            _, success = check_balance(principal_id, expected_balances.get(name, 0))
            balance_verification_success = balance_verification_success and success
        
        results["Balance Verification"] = balance_verification_success
        
        # Re-install vault canister
        results["Re-install Vault"] = test_upgrade()
        
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



if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
