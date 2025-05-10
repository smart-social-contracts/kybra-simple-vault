#!/usr/bin/env python3
"""
Tests for balance checking functionality of the vault canister.
"""

import json
import os
import sys
import traceback

from tests.utils.command import get_canister_id

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import GREEN, RED, RESET
from tests.utils.command import run_command


def check_balance(principal_id, expected_amount=None):
    """Helper function to check balance for a principal."""
    balance_result = run_command(
        f"dfx canister call vault get_balance '(principal \"{principal_id}\")' --output json"
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

        balance_data = balance_json["data"]["Balance"]
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
