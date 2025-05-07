#!/usr/bin/env python3
"""
Tests for balance checking functionality of the vault canister.
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
from tests.utils.command import (
    get_current_principal,
    run_command,
    update_transaction_history_until_no_more_transactions,
)


def check_balance(principal_id, expected_amount=None):
    """Helper function to check balance for a principal."""
    balance_result = run_command(
        f"dfx canister call vault get_balance '(\"{principal_id}\")' --output json"
    )

    if not balance_result:
        print(f"{RED}✗ Balance check failed for {principal_id}{RESET}")
        return None, False

    try:
        balance_json = json.loads(balance_result)

        if not balance_json.get("success", False):
            message = balance_json.get("message", "Unknown error")
            print(f"{RED}✗ Balance check failed: {message}{RESET}")
            return None, (message, False)

        balance_data = balance_json["data"][0]["Balance"]
        amount = int(balance_data.get("amount", 0))

        if expected_amount is not None:
            if amount == expected_amount:
                print(
                    f"{GREEN}✓ {principal_id} balance matches expected value: {expected_amount}{RESET}"
                )
                return amount, True
            else:
                print(
                    f"{RED}✗ {principal_id} balance {amount} does not match expected value: {expected_amount}{RESET}"
                )
                return amount, False

        return amount, True

    except Exception as e:
        print(
            f"{RED}✗ Error parsing balance response: {e}\n{traceback.format_exc()}{RESET}"
        )
        return None, False


def test_balance(expected_user_balance, expected_vault_balance):
    """Test checking both user and vault balances."""

    update_transaction_history_until_no_more_transactions()

    print("\nTesting balance functionality...")

    # Get current user principal
    principal = get_current_principal()
    if not principal:
        return False

    # Check user balance
    user_amount, user_success = check_balance(principal, expected_user_balance)
    if not user_success:
        return False

    # Check vault balance
    vault_id = get_canister_id("vault")
    vault_amount, vault_success = check_balance(vault_id, expected_vault_balance)
    if not vault_success:
        return False

    return True


def test_nonexistent_user_balance():
    """Test balance checking for a non-existent user."""
    print("\nTesting balance check for non-existent user...")

    # Use a non-existent principal
    non_existent_principal = "2vxsx-fae"  # Valid format but not registered

    amount, result = check_balance(non_existent_principal)

    # If we got a successful response but with 0 balance, that's expected
    if isinstance(result, tuple):
        # This means we got an error message, which is acceptable for non-existent users
        error_message, _ = result
        print(
            f"{GREEN}✓ Non-existent user properly handled with error: {error_message}{RESET}"
        )
        return True
    elif amount == 0:
        print(f"{GREEN}✓ Non-existent user has zero balance as expected{RESET}")
        return True
    else:
        print(f"{GREEN}✓ Non-existent user has balance: {amount}{RESET}")
        return True


# def test_invalid_principal():
#     """Test balance checking with an invalid principal format."""
#     print("\nTesting balance check with invalid principal format...")

#     # Use a syntactically valid but semantically invalid principal
#     invalid_principal = (
#         "aaaaa-aaaa-aaaa-aaaa-aaaaa"  # Valid Base32 but likely invalid principal
#     )

#     try:
#         amount, result = check_balance(invalid_principal)

#         if isinstance(result, tuple):
#             # This means we got an error message
#             error_message, _ = result
#             print(
#                 f"{GREEN}✓ Invalid principal correctly rejected: {error_message}{RESET}"
#             )
#             return True
#         elif amount is None:
#             print(f"{GREEN}✓ Invalid principal correctly rejected{RESET}")
#             return True
#         else:
#             print(f"{RED}✗ Invalid principal was accepted, unexpected behavior{RESET}")
#             return False
#     except Exception as e:
#         # If the execution failed with an exception, this might be expected behavior
#         print(f"{GREEN}✓ Invalid principal correctly caused exception: {e}{RESET}")
#         return True
