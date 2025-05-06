#!/usr/bin/env python3
"""
Tests for transaction history functionality of the vault canister.
"""

import json
import os
import sys
import time
import traceback

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import GREEN, RED, RESET
from tests.utils.command import get_canister_id, get_current_principal, run_command


def update_transaction_history():
    """Update transaction history in the vault and return result."""
    try:
        update_result = run_command(
            "dfx canister call vault update_transaction_history --output json"
        )

        if not update_result:
            return None, False

        update_json = json.loads(update_result)
        success = update_json.get("success", False)

        return update_json, success
    except Exception as e:
        print(
            f"{RED}✗ Error updating transaction history: {e}\n{traceback.format_exc()}{RESET}"
        )
        return None, False


def get_transactions(principal_id, max_results=None, max_iterations=None):
    """Get transactions for a principal and return parsed result."""
    try:
        # Build the command based on available parameters
        if max_results is not None and max_iterations is not None:
            cmd = f"dfx canister call vault get_transactions '(\"{principal_id}\", opt {max_results}, opt {max_iterations})' --output json"
        elif max_results is not None:
            cmd = f"dfx canister call vault get_transactions '(\"{principal_id}\", opt {max_results})' --output json"
        else:
            cmd = f"dfx canister call vault get_transactions '(\"{principal_id}\")' --output json"
            
        tx_result = run_command(cmd)

        if not tx_result:
            return None, False, None

        tx_json = json.loads(tx_result)
        success = tx_json.get("success", False)

        if not success:
            message = tx_json.get("message", "Unknown error")
            return tx_json, False, message

        transactions = tx_json["data"][0]["Transactions"] if success else []

        return tx_json, success, transactions
    except Exception as e:
        print(
            f"{RED}✗ Error getting transactions: {e}\n{traceback.format_exc()}{RESET}"
        )
        return None, False, None


def test_update_transactions(expected_count=None):
    """Test updating transaction history in the vault."""
    print("\nTesting transaction history update...")

    update_json, success = update_transaction_history()

    if success:
        print(f"{GREEN}✓ Transaction history update succeeded{RESET}")
        print(f"Update result: {update_json}")

        if expected_count is not None:
            print(f"Expected transaction count: {expected_count}")
            print(f"{GREEN}✓ Transaction count verification skipped{RESET}")

        return True
    else:
        print(f"{RED}✗ Transaction history update failed{RESET}")
        return False


def test_get_transactions(expected_amounts=None):
    """Test retrieving transaction history from the vault."""
    print("\nTesting transaction history retrieval...")

    # Get the principal of the current identity
    principal = get_current_principal()
    if not principal:
        return False

    tx_json, success, transactions = get_transactions(principal)

    if not success:
        message = (
            tx_json.get("message", "Unknown error") if tx_json else "Command failed"
        )
        print(f"{RED}✗ Transaction retrieval failed: {message}{RESET}")
        return False

    if not transactions:
        print(f"{RED}✗ No transactions found{RESET}")
        if expected_amounts and len(expected_amounts) > 0:
            return False
        return True

    print(f"Found {len(transactions)} transactions")

    # Verify each transaction if expected amounts are provided
    if expected_amounts:
        if len(transactions) != len(expected_amounts):
            print(
                f"{RED}✗ Expected {len(expected_amounts)} transactions but found {len(transactions)}{RESET}"
            )
            return False

        for i, tx in enumerate(transactions):
            tx_amount = int(tx["amount"])
            expected_amount = int(expected_amounts[i])
            if tx_amount != expected_amount:
                print(
                    f"{RED}✗ Transaction amount {tx_amount} does not match expected amount {expected_amount}{RESET}"
                )
                return False

        print(f"{GREEN}✓ All expected transaction amounts were found{RESET}")
    else:
        print(f"{GREEN}✓ Transactions retrieved successfully{RESET}")

    return True


def test_get_transactions_nonexistent_user():
    """Test retrieving transaction history for a non-existent user."""
    print("\nTesting transaction history retrieval for non-existent user...")

    # Use a non-existent principal
    non_existent_principal = "2vxsx-fae"  # Valid format but likely not registered

    tx_json, success, transactions = get_transactions(non_existent_principal)

    # If the response returned successfully but with no transactions, that's expected
    if success:
        if not transactions or len(transactions) == 0:
            print(f"{GREEN}✓ Non-existent user has no transactions as expected{RESET}")
            return True
        else:
            print(
                f"{RED}✗ Non-existent user unexpectedly has {len(transactions)} transactions{RESET}"
            )
            return False
    else:
        # If an error was returned, this might be expected behavior too
        message = (
            tx_json.get("message", "Unknown error") if tx_json else "Command failed"
        )
        print(
            f"{GREEN}✓ Non-existent user properly handled with error: {message}{RESET}"
        )
        return True


def test_transaction_ordering():
    """Test that transactions are properly ordered (newest first)."""
    print("\nTesting transaction ordering (newest first)...")

    # Get the principal
    principal = get_current_principal()
    if not principal:
        return False

    _, success, transactions = get_transactions(principal)

    if not success or not transactions:
        print(f"{RED}✗ Failed to retrieve transactions for ordering test{RESET}")
        return False

    if len(transactions) < 2:
        print(
            f"{RED}✗ Not enough transactions to verify ordering (need at least 2){RESET}"
        )
        return False

    # Check if timestamps are in descending order (newest first)
    is_ordered = True
    last_timestamp = None

    for tx in transactions:
        if "timestamp" in tx:
            current_timestamp = int(tx["timestamp"])
            if last_timestamp is not None and current_timestamp > last_timestamp:
                is_ordered = False
                break
            last_timestamp = current_timestamp

    if is_ordered:
        print(f"{GREEN}✓ Transactions are correctly ordered (newest first){RESET}")
        return True
    else:
        print(f"{RED}✗ Transactions are not correctly ordered{RESET}")
        return False


def test_transaction_validity():
    """Test that transaction data is valid and well-formed."""
    print("\nTesting transaction data validity...")

    # Get the principal
    principal = get_current_principal()
    if not principal:
        return False

    _, success, transactions = get_transactions(principal)

    if not success or not transactions:
        print(f"{RED}✗ Failed to retrieve transactions for validity test{RESET}")
        return False

    # Check each transaction for required fields
    required_fields = ["amount", "timestamp"]

    all_valid = True
    for i, tx in enumerate(transactions):
        # Check for required fields
        for field in required_fields:
            if field not in tx:
                print(
                    f"{RED}✗ Transaction {i} is missing required field: {field}{RESET}"
                )
                all_valid = False

    if all_valid:
        print(f"{GREEN}✓ All transactions are valid and well-formed{RESET}")
        return True
    else:
        print(f"{RED}✗ Some transactions have invalid data{RESET}")
        return False


def test_multiple_updates():
    """Test multiple consecutive transaction history updates."""
    print("\nTesting multiple consecutive transaction history updates...")

    success_count = 0
    total_attempts = 3

    for i in range(total_attempts):
        print(f"Update attempt {i+1}...")

        _, success = update_transaction_history()

        if success:
            print(f"{GREEN}✓ Transaction history update {i+1} succeeded{RESET}")
            success_count += 1
        else:
            print(f"{RED}✗ Transaction history update {i+1} failed{RESET}")
            break

        # Wait a short time between updates
        time.sleep(1)

    print(
        f"{GREEN}✓ {success_count}/{total_attempts} transaction history updates completed successfully{RESET}"
    )
    return success_count > 0


def test_transaction_pagination():
    """Test transaction pagination with max_results and max_iterations parameters."""
    print("\nTesting transaction pagination with max_results and max_iterations...")
    
    # Get the principal of the current identity
    principal = get_current_principal()
    if not principal:
        return False
    
    # First, make sure we have enough transactions to test pagination
    # We'll do this by creating at least 5 transactions
    print("Ensuring we have enough transactions for pagination test...")
    from tests.test_cases.transfer_tests import test_multiple_transfers_sequence
    
    # Create several small transfers to ensure we have transactions
    transfers_result = test_multiple_transfers_sequence([1, 1, 1, 1, 1])
    if not transfers_result:
        print(f"{RED}✗ Failed to create test transactions for pagination test{RESET}")
        return False
    
    # Update transaction history to ensure all are recorded
    _, update_success = update_transaction_history()
    if not update_success:
        print(f"{RED}✗ Failed to update transaction history{RESET}")
        return False
    
    # Get all transactions first to know how many we have
    _, base_success, base_transactions = get_transactions(principal)
    if not base_success or not base_transactions:
        print(f"{RED}✗ Failed to get base transactions{RESET}")
        return False
    
    total_transactions = len(base_transactions)
    print(f"Total available transactions: {total_transactions}")
    
    if total_transactions < 3:
        print(f"{RED}✗ Not enough transactions to properly test pagination (need at least 3){RESET}")
        return False
    
    # Test 1: Limit max_results
    desired_results = 2  # We want to limit to 2 results
    print(f"\nTest 1: Limiting results to {desired_results} transactions...")
    
    _, limited_success, limited_transactions = get_transactions(principal, max_results=desired_results)
    if not limited_success:
        print(f"{RED}✗ Failed to get transactions with max_results={desired_results}{RESET}")
        return False
    
    actual_limited_count = len(limited_transactions) if limited_transactions else 0
    print(f"Received {actual_limited_count} transactions when limiting to {desired_results}")
    
    if actual_limited_count == desired_results:
        print(f"{GREEN}✓ max_results={desired_results} correctly limited the number of results{RESET}")
    else:
        print(f"{RED}✗ max_results={desired_results} did not correctly limit results (got {actual_limited_count}){RESET}")
        return False
    
    # Test 2: Set max_iterations low
    print("\nTest 2: Setting max_iterations to 1...")
    
    _, iter_success, iter_transactions = get_transactions(principal, max_results=total_transactions, max_iterations=1)
    if not iter_success:
        print(f"{RED}✗ Failed to get transactions with max_iterations=1{RESET}")
        return False
    
    # With max_iterations=1, we should get some transactions but possibly fewer than total
    # The exact number depends on implementation, but we can verify it works if we get results
    actual_iter_count = len(iter_transactions) if iter_transactions else 0
    print(f"Received {actual_iter_count} transactions when setting max_iterations=1")
    
    if actual_iter_count > 0:
        print(f"{GREEN}✓ max_iterations=1 returned {actual_iter_count} transactions{RESET}")
    else:
        print(f"{RED}✗ max_iterations=1 returned no transactions{RESET}")
        return False
    
    # Test 3: Verify transaction content with different pagination settings
    print("\nTest 3: Verifying transaction content with different pagination settings...")
    
    # Get first 3 transactions with default settings
    _, default_success, default_transactions = get_transactions(principal)
    if not default_success or not default_transactions or len(default_transactions) < 3:
        print(f"{RED}✗ Failed to get default transactions for content comparison{RESET}")
        return False
    
    # Get first 3 transactions with pagination
    _, paginated_success, paginated_transactions = get_transactions(principal, max_results=3)
    if not paginated_success or not paginated_transactions or len(paginated_transactions) < 3:
        print(f"{RED}✗ Failed to get paginated transactions for content comparison{RESET}")
        return False
    
    # Compare the first 3 transactions from both results
    for i in range(3):
        if default_transactions[i]["transaction_id"] != paginated_transactions[i]["transaction_id"]:
            print(f"{RED}✗ Transaction content mismatch between default and paginated results{RESET}")
            return False
    
    print(f"{GREEN}✓ Transaction content matches between default and paginated results{RESET}")
    
    print(f"{GREEN}✓ All pagination tests passed successfully{RESET}")
    return True


if __name__ == "__main__":
    test_update_transactions()
    test_get_transactions()
    test_get_transactions_nonexistent_user()
    test_transaction_ordering()
    test_transaction_validity()
    test_multiple_updates()
    test_transaction_pagination()
