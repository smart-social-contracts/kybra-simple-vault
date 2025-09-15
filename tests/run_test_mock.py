#!/usr/bin/env python3
"""
Mock mode test runner for the vault canister.

This module tests the mock mode capabilities of the vault canister, focusing on:
- Mock entity creation for all supported entity types
- Mock mode validation (enabled/disabled states)
- Integration with existing vault functions
- Error handling for invalid mock data

It deploys the vault in mock mode and runs comprehensive tests.
"""

import sys
import traceback
import json

# Add the parent directory to the Python path to make imports work
sys.path.insert(0, sys.path[0] + "/..")

from tests.utils.colors import print_error, print_ok
from tests.utils.command import (
    run_command,
    run_command_expects_response_obj,
    get_canister_id,
)

# Test configuration constants
TEST_PRINCIPAL = "ah6ac-cc73l-bb2zc-ni7bh-jov4q-roeyj-6k2ob-mkg5j-pequi-vuaa6-2ae"
TEST_BALANCE_AMOUNT = 5000000
TEST_TX_AMOUNT = 1000000


def test_deploy_vault_mock_mode():
    """Test deploying vault in mock mode."""
    print("🚀 Testing vault deployment in mock mode...")
    
    # Deploy vault with mock mode enabled
    result = run_command("dfx deploy vault --argument '(null, null, null, null, opt true)'")
    if not result:
        print_error("Failed to deploy vault in mock mode")
        return False
        
    print_ok("✅ Vault deployed successfully in mock mode")
    return True


def test_deploy_vault_normal_mode():
    """Test deploying vault in normal mode for comparison."""
    print("🚀 Testing vault deployment in normal mode...")
    
    # Stop and delete existing vault
    run_command("dfx canister stop vault")
    run_command("dfx canister delete vault")
    
    # Deploy vault without mock mode
    result = run_command("dfx deploy vault")
    if not result:
        print_error("Failed to deploy vault in normal mode")
        return False
        
    print_ok("✅ Vault deployed successfully in normal mode")
    return True


def test_mock_balance_creation():
    """Test creating mock Balance entities."""
    print("🧪 Testing mock Balance creation...")
    
    balance_data = {
        "_id": TEST_PRINCIPAL,
        "amount": TEST_BALANCE_AMOUNT
    }
    
    json_str = json.dumps(balance_data).replace('"', '\\"')
    command = f'dfx canister call vault mock_entity \'("Balance", "{json_str}")\' --output json'
    result = run_command_expects_response_obj(command)
    
    if not result:
        return False
        
    print_ok("✅ Mock Balance created successfully")
    return True


def test_mock_transaction_creation():
    """Test creating mock VaultTransaction entities."""
    print("🧪 Testing mock VaultTransaction creation...")
    
    tx_data = {
        "_id": "mock_tx_1",
        "principal_from": "mock_ledger",
        "principal_to": TEST_PRINCIPAL,
        "amount": TEST_TX_AMOUNT,
        "timestamp": 1640995200000000000,
        "kind": "mint"
    }
    
    json_str = json.dumps(tx_data).replace('"', '\\"')
    command = f'dfx canister call vault mock_entity \'("VaultTransaction", "{json_str}")\'  --output json'
    result = run_command_expects_response_obj(command)
    
    if not result:
        return False
        
    print_ok("✅ Mock VaultTransaction created successfully")
    return True


def test_mock_balance_creation():
    """Test creating mock Balance entities."""
    print("🧪 Testing mock Balance creation...")
    
    balance_data = {
        "_id": TEST_PRINCIPAL,
        "amount": TEST_BALANCE_AMOUNT
    }
    
    json_str = json.dumps(balance_data).replace('"', '\\"')
    command = f'dfx canister call vault mock_entity \'("Balance", "{json_str}")\'  --output json'
    result = run_command_expects_response_obj(command)
    
    if not result:
        return False
        
    print_ok("✅ Mock Balance created successfully")
    return True


def test_mock_canister_creation():
    """Test creating mock Canisters entities."""
    print("🧪 Testing mock Canisters creation...")
    
    canister_data = {
        "_id": "test_canister",
        "principal": "rdmx6-jaaaa-aaaah-qcaiq-cai"
    }
    
    json_str = json.dumps(canister_data).replace('"', '\\"')
    command = f'dfx canister call vault mock_entity \'("Canisters", "{json_str}")\'  --output json'
    result = run_command_expects_response_obj(command)
    
    if not result:
        return False
        
    print_ok("✅ Mock Canisters created successfully")
    return True


def test_mock_application_data_creation():
    """Test creating mock ApplicationData entities."""
    print("🧪 Testing mock ApplicationData creation...")
    
    app_data = {
        "_id": "test_app_data",
        "admin_principal": TEST_PRINCIPAL,
        "max_results": 50,
        "max_iteration_count": 10,
        "scan_end_tx_id": 100,
        "scan_start_tx_id": 0,
        "scan_oldest_tx_id": 0
    }
    
    json_str = json.dumps(app_data).replace('"', '\\"')
    command = f'dfx canister call vault mock_entity \'("ApplicationData", "{json_str}")\'  --output json'
    result = run_command_expects_response_obj(command)
    
    if not result:
        return False
        
    print_ok("✅ Mock ApplicationData created successfully")
    return True


def test_mock_mode_disabled():
    """Test that mock functions fail when mock mode is disabled."""
    print("🧪 Testing mock mode validation (should fail when disabled)...")
    
    # This should fail since we're in normal mode
    balance_data = {
        "_id": "test_user",
        "amount": 1000
    }
    
    json_str = json.dumps(balance_data).replace('"', '\\"')
    command = f'dfx canister call vault mock_entity \'("Balance", "{json_str}")\' --output json'
    result = run_command(command)
    
    if result and "Mock operations only available in mock mode" in result:
        print_ok("✅ Mock mode validation working correctly")
        return True
    else:
        print_error("❌ Mock mode validation failed - should reject when disabled")
        return False


def test_invalid_entity_type():
    """Test error handling for invalid entity types."""
    print("🧪 Testing invalid entity type handling...")
    
    # Deploy vault in mock mode first
    run_command("dfx canister stop vault")
    run_command("dfx canister delete vault")
    run_command("dfx deploy vault --argument '(null, null, null, null, opt true)'")
    
    invalid_data = {
        "_id": "test",
        "some_field": "value"
    }
    
    json_str = json.dumps(invalid_data).replace('"', '\\"')
    command = f'dfx canister call vault mock_entity \'("InvalidEntity", "{json_str}")\'  --output json'
    result = run_command(command)
    
    if result and "Unknown entity type" in result:
        print_ok("✅ Invalid entity type handling working correctly")
        return True
    else:
        print_error("❌ Invalid entity type should be rejected")
        return False


def test_integration_with_vault_functions():
    """Test that mock entities work with existing vault functions."""
    print("🧪 Testing integration with existing vault functions...")
    
    # First create a mock balance
    balance_data = {
        "_id": TEST_PRINCIPAL,
        "amount": TEST_BALANCE_AMOUNT
    }
    
    json_str = json.dumps(balance_data).replace('"', '\\"')
    command = f'dfx canister call vault mock_entity \'("Balance", "{json_str}")\' '
    run_command(command)
    
    # Now test get_balance function
    command = f"dfx canister call vault get_balance '(principal \"{TEST_PRINCIPAL}\")' --output json"
    result = run_command_expects_response_obj(command)
    
    if not result:
        return False
        
    # Check if the balance matches what we created
    balance_amount = result.get("data", {}).get("Balance", {}).get("amount")
    if balance_amount == str(TEST_BALANCE_AMOUNT):
        print_ok("✅ Mock entities integrate correctly with vault functions")
        return True
    else:
        print_error(f"❌ Expected balance {TEST_BALANCE_AMOUNT}, got {balance_amount}")
        return False


def test_malformed_json():
    """Test error handling for malformed JSON data."""
    print("🧪 Testing malformed JSON handling...")
    
    # Test with malformed JSON
    command = "dfx canister call vault mock_entity '(\"Balance\", \"invalid json\")' --output json"
    result = run_command(command)
    
    if result and ("Failed to create mock entity" in result or "error" in result.lower()):
        print_ok("✅ Malformed JSON handled correctly")
        return True
    else:
        print_error("❌ Malformed JSON should be rejected")
        return False


def main():
    """
    Run the vault mock mode tests.
    
    This function runs a comprehensive test suite for the mock mode functionality.
    """
    print("🧪 Starting Vault Mock Mode Tests")
    print("=" * 50)
    
    tests = [
        ("Deploy vault in mock mode", test_deploy_vault_mock_mode),
        ("Create mock Balance", test_mock_balance_creation),
        ("Create mock VaultTransaction", test_mock_transaction_creation),
        ("Create mock Canisters", test_mock_canister_creation),
        ("Create mock ApplicationData", test_mock_application_data_creation),
        ("Test integration with vault functions", test_integration_with_vault_functions),
        ("Test invalid entity type", test_invalid_entity_type),
        ("Test malformed JSON", test_malformed_json),
        ("Deploy vault in normal mode", test_deploy_vault_normal_mode),
        ("Test mock mode disabled", test_mock_mode_disabled),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print_error(f"❌ FAILED: {test_name}")
        except Exception as e:
            failed += 1
            print_error(f"❌ ERROR in {test_name}: {e}")
            print_error(traceback.format_exc())
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print_ok("🎉 All mock mode tests passed!")
        return True
    else:
        print_error(f"💥 {failed} tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
