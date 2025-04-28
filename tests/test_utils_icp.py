"""Tests for ICRC account encoding and decoding functions in utils_icp."""

import os
import sys

# Add the parent directory to sys.path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vault.vault.utils_icp import encodeIcrcAccount, decodeIcrcAccount
from kybra import Principal

# Test artifacts organized in a data-driven structure
TEST_ARTIFACTS = {
    "principal_only": {
        "input": {
            "principal": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae",
            "subaccount": None
        },
        "output": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae"
    },
    
    "with_subaccount": {
        "input": {
            "principal": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae",
            "subaccount": bytes(range(1, 33))  # bytes 1 through 32 (same as TS example)
        },
        "output": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae-dfxgiyy.102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
    },
    
    "leading_zeros": {
        "input": {
            "principal": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae",
            "subaccount": b'\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\01'  # Leading zeros with single 1 at end
        },
        "output": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae-6cc627i.1"
    }
}

def run_tests():
    """Run simplified tests for ICRC account encoding/decoding functions using test artifacts."""
    print("=== Testing ICRC account encoding/decoding ===")
    
    test_count = 0
    passed = 0
    
    for test_name, test_data in TEST_ARTIFACTS.items():
        test_count += 1
        print(f"\n[TEST] {test_name}")
        
        try:
            # Get test inputs
            principal_text = test_data["input"]["principal"]
            subaccount = test_data["input"]["subaccount"]
            principal = Principal.from_str(principal_text)
            expected_output = test_data["output"]
            
            # Print test details
            print(f"Principal: {principal_text}")
            if subaccount:
                print(f"Subaccount: {subaccount.hex()}")
            else:
                print("Subaccount: None (default)")
            
            # Encode and test
            encoded = encodeIcrcAccount(principal, subaccount)
            print(f"Encoded: {encoded}")
            
            # Verify encoding against expected output
            assert encoded == expected_output, f"Expected {expected_output}, got {encoded}"
            
            # Verify decoding works correctly
            decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
            
            # Verify owner
            assert str(decoded_owner) == principal_text, f"Expected owner {principal_text}, got {decoded_owner}"
            
            # Verify subaccount
            if subaccount is None:
                # Default subaccount should be all zeros
                assert decoded_subaccount == bytes(32), f"Expected default subaccount, got {decoded_subaccount.hex()}"
            else:
                assert decoded_subaccount == subaccount, f"Expected {subaccount.hex()}, got {decoded_subaccount.hex()}"
            
            print(f"✓ {test_name} test passed")
            passed += 1
            
        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
    
    # Print test summary
    print("\n=== Test Summary ===")
    print(f"Passed: {passed}/{test_count} tests")
    
    if passed == test_count:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {test_count - passed} tests failed!")

if __name__ == "__main__":
    run_tests()