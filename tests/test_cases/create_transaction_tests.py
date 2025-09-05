#!/usr/bin/env python3
"""
Tests for create_transaction_record functionality of the vault canister.
"""

import json
import os
import sys
import time
import traceback

from tests.utils.colors import print_error, print_ok
from tests.utils.command import (
    get_canister_id,
    get_current_principal,
    run_command,
    run_command_expects_response_obj,
)

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


def create_transaction_record(
    transaction_id, principal_from, principal_to, amount, timestamp, kind
):
    """Helper function to create a transaction record."""
    cmd = f'dfx canister call vault create_transaction_record \'(record {{ transaction_id = {transaction_id}; principal_from = "{principal_from}"; principal_to = "{principal_to}"; amount = {amount}; timestamp = {timestamp}; kind = "{kind}" }})\' --output json'
    return run_command_expects_response_obj(cmd)


def get_balance(principal_id):
    """Helper function to get balance for a principal."""
    try:
        balance_result = run_command(
            f'dfx canister call vault get_balance \'(principal "{principal_id}")\' --output json'
        )
        if not balance_result:
            return None, False
        
        balance_json = json.loads(balance_result)
        if not balance_json.get("success", False):
            return None, False
            
        balance_data = balance_json["data"]["Balance"]
        amount = int(balance_data.get("amount", 0))
        return amount, True
    except Exception as e:
        print_error(f"Error getting balance: {e}")
        return None, False


def get_transactions(principal_id):
    """Helper function to get transactions for a principal."""
    try:
        cmd = f'dfx canister call vault get_transactions \'(principal "{principal_id}")\' --output json'
        tx_result = run_command(cmd)
        
        if not tx_result:
            return None, False
            
        tx_json = json.loads(tx_result)
        success = tx_json.get("success", False)
        
        if not success:
            return None, False
            
        transactions = tx_json["data"]["Transactions"]
        return transactions, True
    except Exception as e:
        print_error(f"Error getting transactions: {e}")
        return None, False


def test_create_mint_transaction():
    """Test creating a mint transaction record."""
    print("\nTesting mint transaction creation...")
    
    # Get vault canister ID as recipient
    vault_id = get_canister_id("vault")
    if not vault_id:
        print_error("Could not get vault canister ID")
        return False
    
    # Create test parameters
    tx_id = int(time.time() * 1000000)  # Use microsecond timestamp as unique ID
    principal_from = "mint"
    principal_to = vault_id
    amount = 1000000  # 1 million satoshi
    timestamp = int(time.time() * 1000000000)  # nanoseconds
    kind = "mint"
    
    # Get initial balance
    initial_balance, _ = get_balance(vault_id)
    if initial_balance is None:
        initial_balance = 0
    
    # Create the transaction
    result, success, message = create_transaction_record(
        tx_id, principal_from, principal_to, amount, timestamp, kind
    )
    
    if not success:
        print_error(f"Failed to create mint transaction: {message}")
        return False
    
    # Verify the transaction was created and balance updated
    final_balance, balance_success = get_balance(vault_id)
    if not balance_success:
        print_error("Failed to get final balance after mint")
        return False
    
    expected_balance = initial_balance + amount
    if final_balance == expected_balance:
        print_ok(f"Mint transaction created successfully. Balance updated from {initial_balance} to {final_balance}")
        return True
    else:
        print_error(f"Balance mismatch. Expected {expected_balance}, got {final_balance}")
        return False


def test_create_transfer_transaction():
    """Test creating a transfer transaction record."""
    print("\nTesting transfer transaction creation...")
    
    # Get current principal and vault ID
    current_principal = get_current_principal()
    vault_id = get_canister_id("vault")
    
    if not current_principal or not vault_id:
        print_error("Could not get required principals")
        return False
    
    # Create test parameters for deposit (user -> vault)
    tx_id = int(time.time() * 1000000) + 1  # Ensure unique ID
    principal_from = current_principal
    principal_to = vault_id
    amount = 500000  # 0.5 million satoshi
    timestamp = int(time.time() * 1000000000)
    kind = "transfer"
    
    # Get initial balances
    initial_user_balance, _ = get_balance(current_principal)
    initial_vault_balance, _ = get_balance(vault_id)
    
    if initial_user_balance is None:
        initial_user_balance = 0
    if initial_vault_balance is None:
        initial_vault_balance = 0
    
    # Create the transaction
    result, success, message = create_transaction_record(
        tx_id, principal_from, principal_to, amount, timestamp, kind
    )
    
    if not success:
        print_error(f"Failed to create transfer transaction: {message}")
        return False
    
    # Verify balances were updated correctly
    final_user_balance, user_success = get_balance(current_principal)
    final_vault_balance, vault_success = get_balance(vault_id)
    
    if not user_success or not vault_success:
        print_error("Failed to get final balances after transfer")
        return False
    
    expected_user_balance = initial_user_balance + amount  # User balance increases on deposit
    expected_vault_balance = initial_vault_balance + amount  # Vault balance also increases
    
    if final_user_balance == expected_user_balance and final_vault_balance == expected_vault_balance:
        print_ok(f"Transfer transaction created successfully. User: {initial_user_balance} -> {final_user_balance}, Vault: {initial_vault_balance} -> {final_vault_balance}")
        return True
    else:
        print_error(f"Balance mismatch. User expected {expected_user_balance}, got {final_user_balance}. Vault expected {expected_vault_balance}, got {final_vault_balance}")
        return False


def test_create_burn_transaction():
    """Test creating a burn transaction record."""
    print("\nTesting burn transaction creation...")
    
    # Get current principal
    current_principal = get_current_principal()
    if not current_principal:
        print_error("Could not get current principal")
        return False
    
    # Create test parameters
    tx_id = int(time.time() * 1000000) + 2  # Ensure unique ID
    principal_from = current_principal
    principal_to = "burn"
    amount = 100000  # 0.1 million satoshi
    timestamp = int(time.time() * 1000000000)
    kind = "burn"
    
    # Get initial balance
    initial_balance, _ = get_balance(current_principal)
    if initial_balance is None:
        initial_balance = 0
    
    # Create the transaction
    result, success, message = create_transaction_record(
        tx_id, principal_from, principal_to, amount, timestamp, kind
    )
    
    if not success:
        print_error(f"Failed to create burn transaction: {message}")
        return False
    
    # Verify balance was updated
    final_balance, balance_success = get_balance(current_principal)
    if not balance_success:
        print_error("Failed to get final balance after burn")
        return False
    
    expected_balance = initial_balance - amount
    if final_balance == expected_balance:
        print_ok(f"Burn transaction created successfully. Balance updated from {initial_balance} to {final_balance}")
        return True
    else:
        print_error(f"Balance mismatch. Expected {expected_balance}, got {final_balance}")
        return False


def test_validation_errors():
    """Test validation error cases."""
    print("\nTesting validation errors...")
    
    current_principal = get_current_principal()
    if not current_principal:
        print_error("Could not get current principal")
        return False
    
    test_cases = [
        # Negative amount
        {
            "params": (12345, current_principal, current_principal, -100, int(time.time() * 1000000000), "transfer"),
            "expected_error": "Amount must be non-negative"
        },
        # Empty principal_from
        {
            "params": (12346, "", current_principal, 100, int(time.time() * 1000000000), "transfer"),
            "expected_error": "Both principal_from and principal_to must be provided"
        },
        # Invalid transaction kind
        {
            "params": (12347, current_principal, current_principal, 100, int(time.time() * 1000000000), "invalid_kind"),
            "expected_error": "Invalid transaction kind"
        },
        # Duplicate transaction ID (reuse first ID)
        {
            "params": (12345, current_principal, current_principal, 100, int(time.time() * 1000000000), "transfer"),
            "expected_error": "Transaction with ID 12345 already exists"
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases):
        params = test_case["params"]
        expected_error = test_case["expected_error"]
        
        result, success, message = create_transaction_record(*params)
        
        if success:
            print_error(f"Test case {i+1} should have failed but succeeded")
            all_passed = False
        elif expected_error in message:
            print_ok(f"Test case {i+1} correctly failed with expected error")
        else:
            print_error(f"Test case {i+1} failed with unexpected error: {message}")
            all_passed = False
    
    return all_passed


def test_transaction_appears_in_history():
    """Test that created transactions appear in transaction history."""
    print("\nTesting transaction appears in history...")
    
    current_principal = get_current_principal()
    if not current_principal:
        print_error("Could not get current principal")
        return False
    
    # Get initial transaction count
    initial_txs, tx_success = get_transactions(current_principal)
    if not tx_success:
        initial_count = 0
    else:
        initial_count = len(initial_txs)
    
    # Create a new transaction
    tx_id = int(time.time() * 1000000) + 3
    result, success, message = create_transaction_record(
        tx_id, current_principal, "burn", 50000, int(time.time() * 1000000000), "burn"
    )
    
    if not success:
        print_error(f"Failed to create transaction for history test: {message}")
        return False
    
    # Get updated transaction history
    final_txs, tx_success = get_transactions(current_principal)
    if not tx_success:
        print_error("Failed to get transaction history after creation")
        return False
    
    final_count = len(final_txs)
    
    # Check if transaction count increased
    if final_count == initial_count + 1:
        # Look for our specific transaction
        found_tx = False
        for tx in final_txs:
            if tx.get("id") == tx_id:
                found_tx = True
                break
        
        if found_tx:
            print_ok("Transaction successfully appears in history")
            return True
        else:
            print_error("Transaction count increased but specific transaction not found")
            return False
    else:
        print_error(f"Transaction count mismatch. Expected {initial_count + 1}, got {final_count}")
        return False


def run_all_tests():
    """Run all create_transaction_record tests."""
    print("Running create_transaction_record tests...")
    
    tests = [
        test_create_mint_transaction,
        test_create_transfer_transaction,
        test_create_burn_transaction,
        test_validation_errors,
        test_transaction_appears_in_history,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print_error(f"Test {test.__name__} failed")
        except Exception as e:
            print_error(f"Test {test.__name__} crashed: {e}\n{traceback.format_exc()}")
    
    print(f"\nCreate Transaction Record Tests: {passed}/{total} passed")
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
