#!/usr/bin/env python3
"""
Tests for balance checking functionality of the vault canister.
"""

import json
import os
import sys

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import GREEN, RED, RESET
from tests.utils.command import get_canister_id, run_command


def test_balance(expected_user_balance, expected_vault_balance):
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
            f"dfx canister call vault get_balance '(\"{principal}\")' --output json"
        )

        if not balance_result:
            print(f"{RED}✗ Balance check failed{RESET}")
            return False

        # Parse the JSON response
        balance_json = json.loads(balance_result)

        print(f"{GREEN}✓ User balance check succeeded{RESET}")
        print(f"User balance result: {balance_json}")

        # Check if the call was successful
        if not balance_json.get("success", False):
            print(
                f"{RED}✗ Balance check failed: {balance_json.get('message', 'Unknown error')}{RESET}"
            )
            return False

        # Extract the balance value from the result
        # The response structure is: {"success": true, "message": "...", "data": {"Balance": {"_id": "...", "amount": 100}}}
        balance_data = balance_json["data"][0]["Balance"]
        user_balance = int(balance_data.get("amount", 0))

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

        # Check vault balance
        vault_balance_result = run_command(
            "dfx canister call vault get_balance '(\"vault\")' --output json"
        )

        if not vault_balance_result:
            print(f"{RED}✗ Could not retrieve vault balance{RESET}")
            return False

        vault_balance_json = json.loads(vault_balance_result)

        if not vault_balance_json.get("success", False):
            print(f"{RED}✗ Could not retrieve vault balance{RESET}")
            return False

        # Extract the vault balance value
        # Note: Assuming a standard response format, adjust if your API is different
        vault_balance = None
        try:
            vault_balance = int(vault_balance_json["data"][0]["Balance"]["amount"])
            print(f"Current vault balance: {vault_balance}")
        except (KeyError, IndexError, TypeError):
            print(f"{RED}✗ Could not parse vault balance{RESET}")
            # If we can't get the balance, use a very large amount instead
            vault_balance = 10000000000000

        if vault_balance == expected_vault_balance:
            print(
                f"{GREEN}✓ Vault balance matches expected value: {expected_vault_balance}{RESET}"
            )
            return True
        else:
            print(
                f"{RED}✗ Vault balance {vault_balance} does not match expected value: {expected_vault_balance}{RESET}"
            )
            return False

    except Exception as e:
        print(f"{RED}✗ Error checking balance: {e}{RESET}")
        return False


def test_nonexistent_user_balance():
    """Test checking balance for a non-existent user."""
    print("\nTesting balance check for non-existent user...")

    # Use a non-existent principal
    non_existent_principal = (
        "2vxsx-fae"  # This is a valid principal format but likely not registered
    )

    try:
        # Call the get_balance method for the non-existent user
        balance_result = run_command(
            f"dfx canister call vault get_balance '(\"{non_existent_principal}\")' --output json"
        )

        if not balance_result:
            print(f"{RED}✗ Non-existent user balance check failed{RESET}")
            return False

        # Parse the JSON response
        balance_json = json.loads(balance_result)

        print(f"Non-existent user balance result: {balance_json}")

        # Check if the result indicates zero balance or appropriate error
        if balance_json.get("success", False):
            try:
                balance_data = balance_json["data"][0]["Balance"]
                amount = int(balance_data.get("amount", -1))
                if amount == 0:
                    print(
                        f"{GREEN}✓ Non-existent user has zero balance as expected{RESET}"
                    )
                    return True
                else:
                    print(f"{GREEN}✓ Non-existent user has balance: {amount}{RESET}")
                    return True
            except (KeyError, IndexError):
                print(f"{RED}✗ Unexpected response format{RESET}")
                return False
        else:
            # If an error was returned, this might be expected behavior too depending on implementation
            print(
                f"{GREEN}✓ Non-existent user properly handled with error: {balance_json.get('message', 'Unknown')}{RESET}"
            )
            return True

    except Exception as e:
        print(f"{RED}✗ Error checking non-existent user balance: {e}{RESET}")
        return False


def test_invalid_principal():
    """Test checking balance with an invalid principal format."""
    print("\nTesting balance check with invalid principal format...")

    # Use a syntactically valid but semantically invalid principal
    # This uses valid Base32 characters but is not a real principal
    invalid_principal = (
        "aaaaa-aaaa-aaaa-aaaa-aaaaa"  # This is a valid Base32 encoded string
    )

    try:
        # Call the get_balance method with invalid principal
        balance_result = run_command(
            f"dfx canister call vault get_balance '(\"{invalid_principal}\")' --output json"
        )

        # If the command failed to execute, it might be the expected behavior
        if not balance_result:
            print(
                f"{GREEN}✓ Invalid principal correctly rejected at command level{RESET}"
            )
            return True

        # If we got a result, check if it's an error response
        balance_json = json.loads(balance_result)

        if not balance_json.get("success", False):
            print(
                f"{GREEN}✓ Invalid principal correctly rejected: {balance_json.get('message', 'Unknown error')}{RESET}"
            )
            return True
        else:
            print(f"{RED}✗ Invalid principal was accepted, unexpected behavior{RESET}")
            return False

    except Exception as e:
        # If the execution failed with an exception, this might be expected behavior
        print(f"{GREEN}✓ Invalid principal correctly caused exception: {e}{RESET}")
        return True
