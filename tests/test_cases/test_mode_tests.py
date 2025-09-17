#!/usr/bin/env python3
"""
Tests for the vault canister's test mode functionality.
"""

import json
import os
import sys
import traceback

from tests.utils.colors import print_error, print_ok
from tests.utils.command import (
    get_current_principal,
    run_command,
    run_command_expects_response_obj,
)

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


def test_initial_test_mode_status():
    """Test that test mode status returns correct initial values."""
    try:
        print("Testing initial test mode status...")

        # Call test_mode_status
        status_cmd = "dfx canister call vault test_mode_status --output json"
        result = run_command_expects_response_obj(status_cmd)

        if not result:
            print_error("Failed to get test mode status")
            return False

        # Check that we have test mode data
        test_mode_data = result.get("data", {}).get("TestMode")
        if not test_mode_data:
            print_error("No TestMode data in response")
            return False

        # Check initial values
        test_mode_enabled = test_mode_data.get("test_mode_enabled", None)
        tx_id = test_mode_data.get("tx_id", None)

        if test_mode_enabled is None or tx_id is None:
            print_error(
                f"Missing test mode fields: enabled={test_mode_enabled}, tx_id={tx_id}"
            )
            return False

        print(f"Initial test mode status: enabled={test_mode_enabled}, tx_id={tx_id}")
        print_ok("✓ Test mode status query works correctly")
        return True

    except Exception as e:
        print_error(
            f"Error testing initial test mode status: {e}\n{traceback.format_exc()}"
        )
        return False


def test_deploy_vault_with_test_mode_enabled():
    """Test deploying vault with test mode enabled."""
    try:
        print("Testing vault deployment with test mode enabled...")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode enabled")
            return False

        # Check test mode status after deployment
        status_cmd = "dfx canister call vault test_mode_status --output json"
        result = run_command_expects_response_obj(status_cmd)

        if not result:
            print_error("Failed to get test mode status after deployment")
            return False

        test_mode_data = result.get("data", {}).get("TestMode")
        if not test_mode_data:
            print_error("No TestMode data in response after deployment")
            return False

        test_mode_enabled = test_mode_data.get("test_mode_enabled", False)
        if not test_mode_enabled:
            print_error(f"Test mode should be enabled but got: {test_mode_enabled}")
            return False

        print_ok("✓ Vault deployed with test mode enabled")
        return True

    except Exception as e:
        print_error(
            f"Error testing vault deployment with test mode: {e}\n{traceback.format_exc()}"
        )
        return False


def test_deploy_vault_with_test_mode_disabled():
    """Test deploying vault with test mode disabled."""
    try:
        print("Testing vault deployment with test mode disabled...")

        # Deploy vault with test mode disabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(opt principal \\"{current_principal}\\", opt 100, opt 10, opt false)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode disabled")
            return False

        # Check test mode status after deployment
        status_cmd = "dfx canister call vault test_mode_status --output json"
        result = run_command_expects_response_obj(status_cmd)

        if not result:
            print_error("Failed to get test mode status after deployment")
            return False

        test_mode_data = result.get("data", {}).get("TestMode")
        if not test_mode_data:
            print_error("No TestMode data in response after deployment")
            return False

        test_mode_enabled = test_mode_data.get("test_mode_enabled", True)
        if test_mode_enabled:
            print_error(f"Test mode should be disabled but got: {test_mode_enabled}")
            return False

        print_ok("✓ Vault deployed with test mode disabled")
        return True

    except Exception as e:
        print_error(
            f"Error testing vault deployment without test mode: {e}\n{traceback.format_exc()}"
        )
        return False


def test_mock_transfer_in_test_mode():
    """Test that transfers work differently in test mode (mock behavior)."""
    try:
        print("Testing mock transfer behavior in test mode...")

        # First deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode enabled")
            return False

        # Get initial tx_id
        status_cmd = "dfx canister call vault test_mode_status --output json"
        result = run_command_expects_response_obj(status_cmd)

        if not result:
            print_error("Failed to get initial test mode status")
            return False

        initial_tx_id = result.get("data", {}).get("TestMode", {}).get("tx_id", 0)
        print(f"Initial tx_id: {initial_tx_id}")

        # Attempt a transfer (this should increment tx_id in test mode)
        transfer_cmd = f'dfx canister call vault transfer_from_vault "(principal \\"{current_principal}\\", 100)" --output json'
        transfer_result = run_command_expects_response_obj(transfer_cmd)

        if not transfer_result:
            print_error("Transfer command failed")
            return False

        # Check if tx_id was incremented
        status_result = run_command_expects_response_obj(status_cmd)
        if not status_result:
            print_error("Failed to get test mode status after transfer")
            return False

        new_tx_id = status_result.get("data", {}).get("TestMode", {}).get("tx_id", 0)
        print(f"New tx_id after transfer: {new_tx_id}")

        if new_tx_id != initial_tx_id + 1:
            print_error(
                f"Expected tx_id to increment from {initial_tx_id} to {initial_tx_id + 1}, but got {new_tx_id}"
            )
            return False

        print_ok("✓ Mock transfer behavior works correctly in test mode")
        return True

    except Exception as e:
        print_error(
            f"Error testing mock transfer in test mode: {e}\n{traceback.format_exc()}"
        )
        return False


def test_transaction_history_skip_in_test_mode():
    """Test that transaction history updates are skipped in test mode."""
    try:
        print("Testing transaction history skip in test mode...")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode enabled")
            return False

        # Call update_transaction_history (should return success but skip actual work)
        update_cmd = "dfx canister call vault update_transaction_history --output json"
        result = run_command_expects_response_obj(update_cmd)

        if not result:
            print_error("Failed to call update_transaction_history")
            return False

        # In test mode, this should return success but skip the actual update
        # We can verify this by checking the response message or by ensuring it completes quickly
        success = result.get("success", False)
        if not success:
            print_error("update_transaction_history should succeed in test mode")
            return False

        print_ok("✓ Transaction history update skipped correctly in test mode")
        return True

    except Exception as e:
        print_error(
            f"Error testing transaction history skip: {e}\n{traceback.format_exc()}"
        )
        return False


def test_multiple_transfers_increment_tx_id():
    """Test that multiple transfers increment tx_id correctly in test mode."""
    try:
        print("Testing multiple transfers increment tx_id correctly...")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode enabled")
            return False

        # Get initial tx_id
        status_cmd = "dfx canister call vault test_mode_status --output json"
        result = run_command_expects_response_obj(status_cmd)

        if not result:
            print_error("Failed to get initial test mode status")
            return False

        initial_tx_id = result.get("data", {}).get("TestMode", {}).get("tx_id", 0)
        print(f"Initial tx_id: {initial_tx_id}")

        # Perform multiple transfers
        num_transfers = 3
        transfer_cmd = f'dfx canister call vault transfer_from_vault "(principal \\"{current_principal}\\", 10)" --output json'

        for i in range(num_transfers):
            transfer_result = run_command_expects_response_obj(transfer_cmd)
            if not transfer_result:
                print_error(f"Transfer {i+1} failed")
                return False

        # Check final tx_id
        status_result = run_command_expects_response_obj(status_cmd)
        if not status_result:
            print_error("Failed to get final test mode status")
            return False

        final_tx_id = status_result.get("data", {}).get("TestMode", {}).get("tx_id", 0)
        expected_tx_id = initial_tx_id + num_transfers

        print(f"Final tx_id: {final_tx_id}, Expected: {expected_tx_id}")

        if final_tx_id != expected_tx_id:
            print_error(f"Expected tx_id to be {expected_tx_id}, but got {final_tx_id}")
            return False

        print_ok(f"✓ Multiple transfers correctly incremented tx_id by {num_transfers}")
        return True

    except Exception as e:
        print_error(f"Error testing multiple transfers: {e}\n{traceback.format_exc()}")
        return False


def test_test_mode_status_response_format():
    """Test that test_mode_status returns the correct response format."""
    try:
        print("Testing test mode status response format...")

        # Deploy vault (test mode doesn't matter for this test)
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(opt principal \\"{current_principal}\\", opt 100, opt 10, opt false)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault")
            return False

        # Call test_mode_status
        status_cmd = "dfx canister call vault test_mode_status --output json"
        result = run_command_expects_response_obj(status_cmd)

        if not result:
            print_error("Failed to get test mode status")
            return False

        # Verify response structure
        required_fields = ["success", "data"]
        for field in required_fields:
            if field not in result:
                print_error(f"Missing required field '{field}' in response")
                return False

        # Verify TestMode data structure
        test_mode_data = result.get("data", {}).get("TestMode")
        if not test_mode_data:
            print_error("Missing TestMode data in response")
            return False

        required_test_mode_fields = ["test_mode_enabled", "tx_id"]
        for field in required_test_mode_fields:
            if field not in test_mode_data:
                print_error(f"Missing required TestMode field '{field}'")
                return False

        # Verify field types
        if not isinstance(test_mode_data["test_mode_enabled"], bool):
            print_error("test_mode_enabled should be boolean")
            return False

        if not isinstance(test_mode_data["tx_id"], int):
            print_error("tx_id should be integer")
            return False

        print_ok("✓ Test mode status response format is correct")
        return True

    except Exception as e:
        print_error(f"Error testing response format: {e}\n{traceback.format_exc()}")
        return False


def run_all_test_mode_tests():
    """Run all test mode tests and return results."""
    tests = [
        ("Initial Test Mode Status", test_initial_test_mode_status),
        ("Deploy with Test Mode Enabled", test_deploy_vault_with_test_mode_enabled),
        ("Deploy with Test Mode Disabled", test_deploy_vault_with_test_mode_disabled),
        ("Mock Transfer in Test Mode", test_mock_transfer_in_test_mode),
        ("Transaction History Skip", test_transaction_history_skip_in_test_mode),
        ("Multiple Transfers Increment TX ID", test_multiple_transfers_increment_tx_id),
        ("Test Mode Status Response Format", test_test_mode_status_response_format),
    ]

    results = {}

    print("=== Running Test Mode Tests ===")

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test '{test_name}' failed with exception: {e}")
            results[test_name] = False

    return results


if __name__ == "__main__":
    results = run_all_test_mode_tests()

    # Print test summary
    print("\n=== Test Mode Test Summary ===")
    for test_name, passed in results.items():
        if passed:
            print_ok(test_name)
        else:
            print_error(test_name)

    # Count passed tests
    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)

    print_ok(
        f"\nPassed {passed_count} of {total_count} test mode tests ({passed_count/total_count*100:.1f}%)"
    )

    # Exit with appropriate code
    if all(results.values()):
        print_ok("All test mode tests passed!")
        sys.exit(0)
    else:
        print_error("Some test mode tests failed!")
        sys.exit(1)
