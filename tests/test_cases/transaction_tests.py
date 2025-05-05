#!/usr/bin/env python3
"""
Tests for transaction history functionality of the vault canister.
"""

import json
import os
import sys
import traceback

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import GREEN, RED, RESET
from tests.utils.command import run_command


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
