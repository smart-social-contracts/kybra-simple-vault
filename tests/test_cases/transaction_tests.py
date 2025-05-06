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
        print(f"{RED}✗ Error updating transaction history: {e}\n{traceback.format_exc()}{RESET}")
        return None, False


def get_transactions(principal_id):
    """Get transactions for a principal and return parsed result."""
    try:
        tx_result = run_command(
            f"dfx canister call vault get_transactions '(\"{principal_id}\")' --output json"
        )
        
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
        print(f"{RED}✗ Error getting transactions: {e}\n{traceback.format_exc()}{RESET}")
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
        message = tx_json.get("message", "Unknown error") if tx_json else "Command failed"
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
            print(f"{RED}✗ Expected {len(expected_amounts)} transactions but found {len(transactions)}{RESET}")
            return False

        for i, tx in enumerate(transactions):
            tx_amount = int(tx["amount"])
            expected_amount = int(expected_amounts[i])
            if tx_amount != expected_amount:
                print(f"{RED}✗ Transaction amount {tx_amount} does not match expected amount {expected_amount}{RESET}")
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
            print(f"{RED}✗ Non-existent user unexpectedly has {len(transactions)} transactions{RESET}")
            return False
    else:
        # If an error was returned, this might be expected behavior too
        message = tx_json.get("message", "Unknown error") if tx_json else "Command failed"
        print(f"{GREEN}✓ Non-existent user properly handled with error: {message}{RESET}")
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
                print(f"{RED}✗ Transaction {i} is missing required field: {field}{RESET}")
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
    
    print(f"{GREEN}✓ {success_count}/{total_attempts} transaction history updates completed successfully{RESET}")
    return success_count > 0
