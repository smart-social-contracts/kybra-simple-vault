#!/usr/bin/env python3
"""
Tests for balance checking functionality of the vault canister.
"""

import os
import sys

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import GREEN, RED, RESET
from tests.utils.command import run_command


def test_balance(expected_user_balance):
    """Test checking the vault canister's balance."""
    print("\nTesting vault balance functionality...")

    # Get the principal of the current identity
    principal = run_command("dfx identity get-principal")
    if not principal:
        print(f"{RED}✗ Failed to get principal{RESET}")
        return False

    try:
        # Call the get_balance method for the user
        balance_result = run_command(
            f"dfx canister call vault get_balance '(\"{principal}\")'"
        )

        print(f"{GREEN}✓ User balance check succeeded{RESET}")
        print(f"User balance result: {balance_result}")

        # Extract the balance value from the result
        # Example: "(100 : nat)" -> extract "100"
        user_balance = int(balance_result.strip("()").split(":")[0].strip())
        if user_balance == expected_user_balance:
            print(
                f"{GREEN}✓ User balance matches expected value: {expected_user_balance}{RESET}"
            )
            return True
        else:
            print(
                f"{RED}✗ User balance {user_balance} does not match expected value: {expected_user_balance}{RESET}"
            )
            return False

    except Exception as e:
        print(f"{RED}✗ Error checking balance: {e}{RESET}")
        return False
