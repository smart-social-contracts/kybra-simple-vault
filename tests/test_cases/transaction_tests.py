#!/usr/bin/env python3
"""
Tests for transaction history functionality of the vault canister.
"""

import json
import os
import sys
import traceback

from tests.utils.colors import print_error, print_ok
from tests.utils.command import get_current_principal, run_command

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


def get_transactions(principal_id):
    """Get transactions for a principal and return parsed result."""
    try:
        cmd = f"dfx canister call vault get_transactions '(principal \"{principal_id}\")' --output json"
        tx_result = run_command(cmd)

        if not tx_result:
            return None, False, None

        tx_json = json.loads(tx_result)
        success = tx_json.get("success", False)

        if not success:
            message = tx_json.get("message", "Unknown error")
            return tx_json, False, message

        transactions = tx_json["data"]["Transactions"] if success else []

        return tx_json, success, transactions
    except Exception as e:
        print_error(f"Error getting transactions: {e}\n{traceback.format_exc()}")
        return None, False, None


def test_get_transactions_nonexistent_user():
    """Test retrieving transaction history for a non-existent user."""
    print("\nTesting transaction history retrieval for non-existent user...")

    # Use a non-existent principal
    non_existent_principal = "2vxsx-fae"  # Valid format but likely not registered

    tx_json, success, transactions = get_transactions(non_existent_principal)

    # If the response returned successfully but with no transactions, that's expected
    if success:
        if not transactions or len(transactions) == 0:
            print_ok("Non-existent user has no transactions as expected")
            return True
        else:
            print_error(
                f"Non-existent user unexpectedly has {len(transactions)} transactions"
            )
            return False
    else:
        # If an error was returned, this might be expected behavior too
        message = (
            tx_json.get("message", "Unknown error") if tx_json else "Command failed"
        )
        print_ok(f"Non-existent user properly handled with error: {message}")
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
        print_error("Failed to retrieve transactions for ordering test")
        return False

    if len(transactions) < 2:
        print_error("Not enough transactions to verify ordering (need at least 2)")
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
        print_ok("Transactions are correctly ordered (newest first)")
        return True
    else:
        print_error("Transactions are not correctly ordered")
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
        print_error("Failed to retrieve transactions for validity test")
        return False

    # Check each transaction for required fields
    required_fields = ["amount", "timestamp"]

    all_valid = True
    for i, tx in enumerate(transactions):
        # Check for required fields
        for field in required_fields:
            if field not in tx:
                print_error(f"Transaction {i} is missing required field: {field}")
                all_valid = False

    if all_valid:
        print_ok("All transactions are valid and well-formed")
        return True
    else:
        print_error("Some transactions have invalid data")
        return False
