#!/usr/bin/env python3
"""
Tests for transaction history functionality of the vault canister.
"""

import json
import os
import sys
import traceback
import time

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.command import run_command, get_canister_id
from tests.utils.colors import GREEN, RED, RESET


def test_update_transactions(expected_count=None):
    """Test updating transaction history in the vault."""
    print("\nTesting transaction history update...")

    # Get the principal of the current identity
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False

    try:
        # Update transaction history with --output json
        update_result = run_command(
            "dfx canister call vault update_transaction_history --output json"
        )

        if update_result:
            # Parse JSON result
            update_json = json.loads(update_result)
            print(f"{GREEN}✓ Transaction history update succeeded{RESET}")
            print(f"Update result: {update_json}")

            # Verify the expected count if provided
            if expected_count is not None:
                # Try to extract the count from the update result if it's returned
                print(f"Expected transaction count: {expected_count}")
                # This is just a placeholder check
                print(f"{GREEN}✓ Transaction count verification skipped{RESET}")

            return True
        else:
            print(f"{RED}✗ Transaction history update failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error updating transaction history: {e}{RESET}")
        return False


def test_get_transactions(expected_amounts=None):
    """Test retrieving transaction history from the vault."""
    print("\nTesting transaction history retrieval...")

    # Get the principal of the current identity
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False

    try:
        # Get transaction history
        tx_result = run_command(
            f"dfx canister call vault get_transactions '(\"{principal}\")' --output json"
        )

        tx_result = json.loads(tx_result)
        print("tx_result", tx_result)

        # Extract transactions from the response
        # The response structure is: {"success": true, "message": "...", "data": {"Transactions": {"transactions": [...]}}}
        if not tx_result.get("success", False):
            print(
                f"{RED}✗ Transaction retrieval failed: {tx_result.get('message', 'Unknown error')}{RESET}"
            )
            return False

        transactions = tx_result["data"][0]["Transactions"]

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

    except Exception as e:
        print(
            f"{RED}✗ Error retrieving transaction history: {e}\n{traceback.format_exc()}{RESET}"
        )
        return False


def test_get_transactions_nonexistent_user():
    """Test retrieving transaction history for a non-existent user."""
    print("\nTesting transaction history retrieval for non-existent user...")

    # Use a non-existent principal
    non_existent_principal = "2vxsx-fae"  # This is a valid principal format but likely not registered

    try:
        # Get transaction history
        tx_result = run_command(
            f"dfx canister call vault get_transactions '(\"{non_existent_principal}\")' --output json"
        )

        if not tx_result:
            print(f"{RED}✗ Transaction retrieval for non-existent user failed{RESET}")
            return False

        tx_result = json.loads(tx_result)
        print(f"Non-existent user transaction result: {tx_result}")

        # Check if the response indicates no transactions (empty array or appropriate error)
        if tx_result.get("success", False):
            try:
                transactions = tx_result["data"][0]["Transactions"]
                if not transactions or len(transactions) == 0:
                    print(f"{GREEN}✓ Non-existent user has no transactions as expected{RESET}")
                    return True
                else:
                    print(f"{RED}✗ Non-existent user unexpectedly has {len(transactions)} transactions{RESET}")
                    return False
            except (KeyError, IndexError):
                print(f"{RED}✗ Unexpected response format{RESET}")
                return False
        else:
            # If an error was returned, this might be expected behavior too
            print(f"{GREEN}✓ Non-existent user properly handled with error: {tx_result.get('message', 'Unknown')}{RESET}")
            return True

    except Exception as e:
        print(f"{RED}✗ Error retrieving transaction history for non-existent user: {e}{RESET}")
        return False


def test_transaction_ordering():
    """Test that transactions are properly ordered (newest first)."""
    print("\nTesting transaction ordering...")

    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False

    try:
        # Get transactions
        tx_result = run_command(
            f"dfx canister call vault get_transactions '(\"{principal}\")' --output json"
        )

        if not tx_result:
            print(f"{RED}✗ Transaction retrieval failed{RESET}")
            return False

        tx_result = json.loads(tx_result)
        if not tx_result.get("success", False):
            print(
                f"{RED}✗ Transaction retrieval failed: {tx_result.get('message', 'Unknown error')}{RESET}"
            )
            return False

        transactions = tx_result["data"][0]["Transactions"]

        if not transactions or len(transactions) < 2:
            print(f"{RED}✗ Not enough transactions to verify ordering (need at least 2){RESET}")
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

    except Exception as e:
        print(f"{RED}✗ Error checking transaction ordering: {e}{RESET}")
        return False


def test_transaction_validity():
    """Test that transaction data is valid and well-formed."""
    print("\nTesting transaction data validity...")

    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False

    try:
        # Get transactions
        tx_result = run_command(
            f"dfx canister call vault get_transactions '(\"{principal}\")' --output json"
        )

        if not tx_result:
            print(f"{RED}✗ Transaction retrieval failed{RESET}")
            return False

        tx_result = json.loads(tx_result)
        if not tx_result.get("success", False):
            print(
                f"{RED}✗ Transaction retrieval failed: {tx_result.get('message', 'Unknown error')}{RESET}"
            )
            return False

        transactions = tx_result["data"][0]["Transactions"]

        if not transactions:
            print(f"{RED}✗ No transactions found to validate{RESET}")
            return False

        # Check each transaction for required fields
        required_fields = ["amount", "timestamp"]  # Add other required fields

        all_valid = True
        for i, tx in enumerate(transactions):
            # Check for required fields
            for field in required_fields:
                if field not in tx:
                    print(f"{RED}✗ Transaction {i} is missing required field: {field}{RESET}")
                    all_valid = False

        if all_valid:
            print(f"{GREEN}✓ All transactions are valid and well-formed{RESET}")
            return True
        else:
            print(f"{RED}✗ Some transactions have invalid data{RESET}")
            return False

    except Exception as e:
        print(f"{RED}✗ Error validating transaction data: {e}{RESET}")
        return False


def test_multiple_updates():
    """Test multiple consecutive transaction history updates."""
    print("\nTesting multiple consecutive transaction history updates...")

    success = True

    try:
        # Perform multiple updates in a row
        for i in range(3):
            print(f"Update attempt {i+1}...")
            update_result = run_command(
                "dfx canister call vault update_transaction_history --output json"
            )

            if not update_result:
                print(f"{RED}✗ Transaction history update {i+1} failed{RESET}")
                success = False
                break

            # Parse JSON result
            update_json = json.loads(update_result)
            if not update_json.get("success", False):
                print(f"{RED}✗ Transaction history update {i+1} failed: {update_json.get('message', 'Unknown error')}{RESET}")
                success = False
                break

            print(f"{GREEN}✓ Transaction history update {i+1} succeeded{RESET}")

            # Wait a short time between updates
            time.sleep(1)

        if success:
            print(f"{GREEN}✓ Multiple transaction history updates completed successfully{RESET}")
        else:
            print(f"{RED}✗ Multiple transaction history updates failed{RESET}")

        return success

    except Exception as e:
        print(f"{RED}✗ Error during multiple transaction history updates: {e}{RESET}")
        return False
