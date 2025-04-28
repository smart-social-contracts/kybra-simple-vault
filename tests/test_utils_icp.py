"""Tests for ICRC account encoding and decoding functions in utils_icp."""

import os
import sys

# Add the parent directory to sys.path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vault.vault.utils_icp import encodeIcrcAccount, decodeIcrcAccount
from kybra import Principal

def run_tests():
    """Run all tests for ICRC account encoding/decoding functions"""
    print("=== Testing ICRC account encoding/decoding ===")
    
    test_count = 0
    passed = 0
    
    # Test 1: Default subaccount encoding
    print("\n[TEST] Default subaccount encoding")
    try:
        # Create a test principal
        principal_text = "2vxsx-fae"  # Example principal
        principal = Principal.from_str(principal_text)
        
        # Encode the account with default subaccount
        encoded = encodeIcrcAccount(principal)
        
        # With default subaccount, output should be the principal text
        assert encoded == principal_text, f"Expected {principal_text}, got {encoded}"
        print(f"✓ Encoded to: {encoded}")
        
        # Decode and verify the result
        decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
        
        # Owner should match the original principal
        assert str(decoded_owner) == str(principal), f"Expected {principal}, got {decoded_owner}"
        print(f"✓ Decoded owner matches: {decoded_owner}")
        
        # Default subaccount should be all zeros
        assert decoded_subaccount == b"\x00" * 32, f"Expected 32 zero bytes, got {decoded_subaccount}"
        print(f"✓ Default subaccount is correct: {decoded_subaccount[:3]}...{decoded_subaccount[-3:]}")
        
        test_count += 1
        passed += 1
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        test_count += 1
    
    # Test 2: Specific subaccount encoding
    print("\n[TEST] Specific subaccount encoding")
    try:
        # Create a test principal
        principal = Principal.from_str("2vxsx-fae")
        
        # Create a test subaccount with a non-zero value to ensure it's encoded
        subaccount = bytes([1]) + bytes([0]) * 31  # First byte is 1, rest are 0
        
        # Encode the account
        encoded = encodeIcrcAccount(principal, subaccount)
        
        # Verify it's a string and has the expected format with hyphen and period
        assert isinstance(encoded, str), f"Expected string, got {type(encoded)}"
        assert "-" in encoded, f"Expected hyphen in {encoded}"
        assert "." in encoded, f"Expected period in {encoded}"
        print(f"✓ Encoded with subaccount to: {encoded}")
        
        # Decode and verify
        decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
        
        # Owner should match
        assert str(decoded_owner) == str(principal), f"Expected {principal}, got {decoded_owner}"
        print(f"✓ Decoded owner matches: {decoded_owner}")
        
        # Subaccount should match
        assert decoded_subaccount == subaccount, f"Expected {subaccount}, got {decoded_subaccount}"
        print(f"✓ Custom subaccount preserved: {decoded_subaccount[:3]}...{decoded_subaccount[-3:]}")
        
        test_count += 1
        passed += 1
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        test_count += 1
    
    # Test 3: Invalid subaccount format
    print("\n[TEST] Invalid subaccount format")
    try:
        # Invalid format: missing the subaccount part after the dot
        invalid_encoded = "2vxsx-fae-abcde"
        
        # Should raise ValueError
        try:
            decoded = decodeIcrcAccount(invalid_encoded)
            # If we get here, the test failed
            print(f"✗ Expected ValueError, but got: {decoded}")
            test_count += 1
        except ValueError:
            # Expected error
            print("✓ Correctly rejected invalid format")
            test_count += 1
            passed += 1
    except Exception as e:
        print(f"✗ Test failed unexpectedly: {str(e)}")
        test_count += 1
    
    # Test 4: Invalid text format
    print("\n[TEST] Invalid text format")
    try:
        # Invalid format: doesn't follow the expected pattern
        invalid_encoded = "not-a-valid-account"
        
        # Should raise ValueError
        try:
            decoded = decodeIcrcAccount(invalid_encoded)
            # If we get here, the test failed
            print(f"✗ Expected ValueError, but got: {decoded}")
            test_count += 1
        except ValueError:
            # Expected error
            print("✓ Correctly rejected invalid account text")
            test_count += 1
            passed += 1
    except Exception as e:
        print(f"✗ Test failed unexpectedly: {str(e)}")
        test_count += 1
    
    # Test 5: Round-trip with various principals
    print("\n[TEST] Round-trip with various principals")
    try:
        # Test with various principal IDs
        test_principals = [
            "2vxsx-fae",  # Short
            "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe",  # Long
            "aaaaa-aa"  # IC management canister
        ]
        
        for principal_text in test_principals:
            principal = Principal.from_str(principal_text)
            print(f"\nTesting with principal: {principal_text}")
            
            # Test with default subaccount
            encoded = encodeIcrcAccount(principal)
            decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
            
            assert str(decoded_owner) == str(principal), f"Expected {principal}, got {decoded_owner}"
            assert decoded_subaccount == b"\x00" * 32, f"Expected 32 zero bytes, got {decoded_subaccount}"
            print(f"✓ Default subaccount roundtrip successful")
            
            # Test with custom subaccount (ensure first byte is non-zero)
            custom_subaccount = bytes([1]) + bytes(range(1, 32))  # Non-zero first byte
            encoded = encodeIcrcAccount(principal, custom_subaccount)
            decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
            
            assert str(decoded_owner) == str(principal), f"Expected {principal}, got {decoded_owner}"
            assert decoded_subaccount == custom_subaccount, f"Expected {custom_subaccount}, got {decoded_subaccount}"
            print(f"✓ Custom subaccount roundtrip successful")
        
        test_count += 1
        passed += 1
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        test_count += 1
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}/{test_count} tests")
    
    if passed == test_count:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {test_count - passed} tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)