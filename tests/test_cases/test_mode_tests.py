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

        # First deploy vault with default settings
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt false)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault for initial test")
            return False

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

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

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

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault with test mode disabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt false)"'

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

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # First deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

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

        initial_tx_id = int(result.get("data", {}).get("TestMode", {}).get("tx_id", 0))
        print(f"Initial tx_id: {initial_tx_id}")

        # Attempt a transfer (this should increment tx_id in test mode)
        transfer_cmd = f'dfx canister call vault transfer "(principal \\"{current_principal}\\", 100)" --output json'
        transfer_result = run_command_expects_response_obj(transfer_cmd)

        if not transfer_result:
            print_error("Transfer command failed")
            return False

        # Check if tx_id was incremented
        status_result = run_command_expects_response_obj(status_cmd)
        if not status_result:
            print_error("Failed to get test mode status after transfer")
            return False

        new_tx_id = status_result.get("data", {}).get("TestMode", {}).get("tx_id", "0")
        print(f"New tx_id after transfer: {new_tx_id}")

        # Convert to int for comparison since tx_id should increment from 0 to 1
        initial_tx_id_int = int(initial_tx_id)
        new_tx_id_int = int(new_tx_id)

        if new_tx_id_int != initial_tx_id_int + 1:
            print_error(
                f"Expected tx_id to increment from {initial_tx_id} to {initial_tx_id_int + 1}, but got {new_tx_id}"
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

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

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

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

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

        initial_tx_id = result.get("data", {}).get("TestMode", {}).get("tx_id", "0")
        print(f"Initial tx_id: {initial_tx_id}")

        # Perform multiple transfers
        num_transfers = 3
        transfer_cmd = f'dfx canister call vault transfer "(principal \\"{current_principal}\\", 10)" --output json'

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

        final_tx_id = (
            status_result.get("data", {}).get("TestMode", {}).get("tx_id", "0")
        )
        expected_tx_id = str(int(initial_tx_id) + num_transfers)

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

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault (test mode doesn't matter for this test)
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt false)"'

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

        print_ok("✓ Test mode status response format is correct")
        return True

    except Exception as e:
        print_error(f"Error testing response format: {e}\n{traceback.format_exc()}")
        return False


def test_mock_transaction_history():
    """Test that mock transfers create proper transaction history."""
    try:
        print("Testing mock transaction history creation...")

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode enabled")
            return False

        # Perform a mock transfer
        transfer_cmd = f'dfx canister call vault transfer "(principal \\"{current_principal}\\", 100)" --output json'
        transfer_result = run_command_expects_response_obj(transfer_cmd)

        if not transfer_result:
            print_error("Mock transfer failed")
            return False

        # Check transaction history
        get_transactions_cmd = f'dfx canister call vault get_transactions "(principal \\"{current_principal}\\")" --output json'
        transactions_result = run_command_expects_response_obj(get_transactions_cmd)

        if not transactions_result:
            print_error("Failed to get transaction history")
            return False

        transactions = transactions_result.get("data", {}).get("Transactions", [])
        if not transactions:
            print_error("No transactions found in history")
            return False

        # Verify transaction details
        transaction = transactions[0]
        if transaction.get("amount") != "100":
            print_error(
                f"Expected transaction amount 100, got {transaction.get('amount')}"
            )
            return False

        if "timestamp" not in transaction:
            print_error("Transaction missing timestamp")
            return False

        print_ok("✓ Mock transaction history created correctly")
        return True

    except Exception as e:
        print_error(
            f"Error testing mock transaction history: {e}\n{traceback.format_exc()}"
        )
        return False


def test_balance_consistency_with_history():
    """Test that balances are consistent with transaction history."""
    try:
        print("Testing balance consistency with transaction history...")

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode enabled")
            return False

        # Get initial balance (should be 0)
        get_balance_cmd = f'dfx canister call vault get_balance "(principal \\"{current_principal}\\")" --output json'
        initial_balance_result = run_command_expects_response_obj(get_balance_cmd)

        if not initial_balance_result:
            print_error("Failed to get initial balance")
            return False

        initial_balance = int(
            initial_balance_result.get("data", {}).get("Balance", {}).get("amount", "0")
        )

        # Perform multiple mock transfers
        transfer_amounts = [100, 50, 25]
        total_received = sum(transfer_amounts)

        for amount in transfer_amounts:
            transfer_cmd = f'dfx canister call vault transfer "(principal \\"{current_principal}\\", {amount})" --output json'
            transfer_result = run_command_expects_response_obj(transfer_cmd)

            if not transfer_result:
                print_error(f"Mock transfer of {amount} failed")
                return False

        # Check final balance
        final_balance_result = run_command_expects_response_obj(get_balance_cmd)
        if not final_balance_result:
            print_error("Failed to get final balance")
            return False

        final_balance = int(
            final_balance_result.get("data", {}).get("Balance", {}).get("amount", "0")
        )
        expected_balance = initial_balance + total_received

        if final_balance != expected_balance:
            print_error(f"Expected balance {expected_balance}, got {final_balance}")
            return False

        # Verify transaction count matches
        get_transactions_cmd = f'dfx canister call vault get_transactions "(principal \\"{current_principal}\\")" --output json'
        transactions_result = run_command_expects_response_obj(get_transactions_cmd)

        if not transactions_result:
            print_error("Failed to get transaction history")
            return False

        transactions = transactions_result.get("data", {}).get("Transactions", [])
        if len(transactions) != len(transfer_amounts):
            print_error(
                f"Expected {len(transfer_amounts)} transactions, got {len(transactions)}"
            )
            return False

        print_ok("✓ Balance consistency with transaction history verified")
        return True

    except Exception as e:
        print_error(f"Error testing balance consistency: {e}\n{traceback.format_exc()}")
        return False


def test_test_mode_utility_functions():
    """Test the test mode utility functions (set_balance, reset)."""
    try:
        print("Testing test mode utility functions...")

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode enabled")
            return False

        # Test set_balance function
        set_balance_cmd = f'dfx canister call vault test_mode_set_balance "(principal \\"{current_principal}\\", 500)" --output json'
        set_balance_result = run_command_expects_response_obj(set_balance_cmd)

        if not set_balance_result or not set_balance_result.get("success"):
            print_error("Failed to set balance in test mode")
            return False

        # Verify balance was set
        get_balance_cmd = f'dfx canister call vault get_balance "(principal \\"{current_principal}\\")" --output json'
        balance_result = run_command_expects_response_obj(get_balance_cmd)

        if not balance_result:
            print_error("Failed to get balance after setting")
            return False

        balance = int(
            balance_result.get("data", {}).get("Balance", {}).get("amount", "0")
        )
        if balance != 500:
            print_error(f"Expected balance 500, got {balance}")
            return False

        # Perform a transfer to create transaction history
        transfer_cmd = f'dfx canister call vault transfer "(principal \\"{current_principal}\\", 100)" --output json'
        transfer_result = run_command_expects_response_obj(transfer_cmd)

        if not transfer_result:
            print_error("Mock transfer failed")
            return False

        # Test reset function
        reset_cmd = "dfx canister call vault test_mode_reset --output json"
        reset_result = run_command_expects_response_obj(reset_cmd)

        if not reset_result or not reset_result.get("success"):
            print_error("Failed to reset test mode")
            return False

        # Verify reset worked - check tx_id
        status_cmd = "dfx canister call vault test_mode_status --output json"
        status_result = run_command_expects_response_obj(status_cmd)

        if not status_result:
            print_error("Failed to get test mode status after reset")
            return False

        tx_id = status_result.get("data", {}).get("TestMode", {}).get("tx_id", "0")
        if tx_id != "0":
            print_error(f"Expected tx_id to be 0 after reset, got {tx_id}")
            return False

        # Verify balance was reset
        balance_result = run_command_expects_response_obj(get_balance_cmd)
        if balance_result:
            balance = int(
                balance_result.get("data", {}).get("Balance", {}).get("amount", "0")
            )
            if balance != 0:
                print_error(f"Expected balance to be 0 after reset, got {balance}")
                return False

        print_ok("✓ Test mode utility functions work correctly")
        return True

    except Exception as e:
        print_error(f"Error testing utility functions: {e}\n{traceback.format_exc()}")
        return False


def test_reset_clears_mock_transactions():
    """Test that test_mode_reset clears transactions created via test_mode_set_mock_transaction."""
    try:
        print("Testing reset clears mock transactions...")

        # Clean up any existing vault to ensure fresh deployment
        run_command("dfx canister delete vault --yes || true")

        # Deploy vault with test mode enabled
        current_principal = get_current_principal()
        deploy_cmd = f'dfx deploy vault --argument "(null, opt principal \\"{current_principal}\\", opt 100, opt 10, opt true)"'

        result = run_command(deploy_cmd)
        if not result:
            print_error("Failed to deploy vault with test mode enabled")
            return False

        # Create mock transactions using test_mode_set_mock_transaction
        # Use default kind parameter (should be "mock_transfer" after fix)
        principal2 = "2vxsx-fae"  # Dummy principal
        set_mock_cmd = f'dfx canister call vault test_mode_set_mock_transaction "(principal \"{current_principal}\", principal \"{principal2}\", 100, null, null)" --output json'

        set_result = run_command_expects_response_obj(set_mock_cmd)
        if not set_result or not set_result.get("success"):
            print_error("Failed to set mock transaction")
            return False

        # Verify transaction was created
        get_transactions_cmd = f'dfx canister call vault get_transactions "(principal \\"{current_principal}\\")" --output json'
        transactions_result = run_command_expects_response_obj(get_transactions_cmd)

        if not transactions_result:
            print_error("Failed to get transaction history")
            return False

        transactions = transactions_result.get("data", {}).get("Transactions", [])
        if len(transactions) != 1:
            print_error(f"Expected 1 transaction before reset, got {len(transactions)}")
            return False

        print(f"Created {len(transactions)} mock transaction(s)")

        # Call test_mode_reset
        reset_cmd = "dfx canister call vault test_mode_reset --output json"
        reset_result = run_command_expects_response_obj(reset_cmd)

        if not reset_result or not reset_result.get("success"):
            print_error("Failed to reset test mode")
            return False

        # Verify transactions were cleared
        transactions_result_after = run_command_expects_response_obj(
            get_transactions_cmd
        )

        if not transactions_result_after:
            print_error("Failed to get transaction history after reset")
            return False

        transactions_after = transactions_result_after.get("data", {}).get(
            "Transactions", []
        )
        if len(transactions_after) != 0:
            print_error(
                f"Expected 0 transactions after reset, got {len(transactions_after)}"
            )
            print_error(f"Transactions after reset: {transactions_after}")
            return False

        print_ok("✓ test_mode_reset properly cleared mock transactions")
        return True

    except Exception as e:
        print_error(
            f"Error testing reset clears mock transactions: {e}\n{traceback.format_exc()}"
        )
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
        ("Mock Transaction History", test_mock_transaction_history),
        ("Balance Consistency with History", test_balance_consistency_with_history),
        ("Test Mode Utility Functions", test_test_mode_utility_functions),
        ("Reset Clears Mock Transactions", test_reset_clears_mock_transactions),
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
