"""Tests for ICRC account encoding and decoding functions in utils_icp."""

import os
import sys
import random

# Add the parent directory to sys.path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vault.vault.utils_icp import encodeIcrcAccount, decodeIcrcAccount, compute_crc
from kybra import Principal

# Test constants - modify these to test with different values
TEST_PRINCIPALS = [
    "2vxsx-fae",                                                     # Short principal
    "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe",  # Long principal
    "aaaaa-aa"                                                      # IC management canister
]

# Create different patterns of subaccounts for testing
DEFAULT_SUBACCOUNT = bytes(32)  # 32 zeros
SEQUENTIAL_SUBACCOUNT = bytes(range(1, 33))  # bytes 1 through 32
LEADING_ZEROS_SUBACCOUNT = bytes([0, 0, 0, 0, 1, 2, 3, 4]) + bytes(24)  # Leading zeros followed by pattern

# Invalid account format examples
INVALID_FORMATS = [
    "",                     # Empty string
    "not-a-valid-account",  # Invalid principal
    "2vxsx-fae-checksumonly",  # Missing dot and subaccount
    "2vxsx-fae.",           # Missing subaccount after dot
    ".01020304"             # Missing principal
]

def create_random_subaccount():
    """Create a random subaccount with non-zero first byte"""
    first_byte = random.randint(1, 255)  # Ensure non-zero first byte
    return bytes([first_byte]) + os.urandom(31)  # Random 31 remaining bytes

def run_tests():
    """Run all tests for ICRC account encoding/decoding functions"""
    print("=== Testing ICRC account encoding/decoding ===")
    
    test_count = 0
    passed = 0
    
    # Test 1: Default subaccount encoding
    print("\n[TEST] Default subaccount encoding")
    try:
        # Use first test principal
        principal_text = TEST_PRINCIPALS[0]
        principal = Principal.from_str(principal_text)
        
        # Encode with default subaccount (None)
        encoded1 = encodeIcrcAccount(principal)
        assert encoded1 == principal_text, f"Expected {principal_text}, got {encoded1}"
        print(f"✓ Encoded with None subaccount to: {encoded1}")
        
        # Encode with empty subaccount
        encoded2 = encodeIcrcAccount(principal, bytes(0))
        assert encoded2 == principal_text, f"Expected {principal_text}, got {encoded2}"
        print(f"✓ Encoded with empty subaccount to: {encoded2}")
        
        # Encode with zero subaccount
        encoded3 = encodeIcrcAccount(principal, bytes(32))
        assert encoded3 == principal_text, f"Expected {principal_text}, got {encoded3}"
        print(f"✓ Encoded with zero subaccount to: {encoded3}")
        
        # Decode and verify the result
        decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded1)
        
        # Owner should match the original principal
        assert str(decoded_owner) == str(principal), f"Expected {principal}, got {decoded_owner}"
        print(f"✓ Decoded owner matches: {decoded_owner}")
        
        # Default subaccount should be all zeros
        assert decoded_subaccount == bytes(32), f"Expected 32 zero bytes, got {decoded_subaccount}"
        print(f"✓ Default subaccount is correct: {decoded_subaccount[:3]}...{decoded_subaccount[-3:]}")
        
        test_count += 1
        passed += 1
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        test_count += 1
    
    # Test 2: Specific subaccount encoding
    print("\n[TEST] Specific subaccount encoding")
    try:
        # Use first test principal
        principal = Principal.from_str(TEST_PRINCIPALS[0])
        
        # Use the sequential subaccount pattern
        subaccount = SEQUENTIAL_SUBACCOUNT
        
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
    
    # Test 3: Leading zeros in subaccount
    print("\n[TEST] Leading zeros in subaccount")
    try:
        principal = Principal.from_str(TEST_PRINCIPALS[0])
        
        # Use the subaccount with leading zeros
        subaccount = LEADING_ZEROS_SUBACCOUNT
        
        # Encode the account
        encoded = encodeIcrcAccount(principal, subaccount)
        
        # Verify format
        parts = encoded.split(".")
        assert len(parts) == 2, f"Expected format with dot separator, got {encoded}"
        
        # Subaccount hex part should not have leading zeros
        subaccount_hex = parts[1]
        assert not subaccount_hex.startswith("0"), f"Should not have leading zeros: {subaccount_hex}"
        
        print(f"✓ Encoded with leading zero subaccount to: {encoded}")
        
        # Decode and verify roundtrip
        decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
        assert decoded_subaccount == subaccount, f"Roundtrip failed: {decoded_subaccount} != {subaccount}"
        print(f"✓ Roundtrip successful with leading zeros")
        
        test_count += 1
        passed += 1
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        test_count += 1
    
    # Test 4: Checksum validation
    print("\n[TEST] Checksum validation")
    try:
        principal = Principal.from_str(TEST_PRINCIPALS[0])
        subaccount = SEQUENTIAL_SUBACCOUNT
        
        # Compute valid checksum
        checksum = compute_crc(principal, subaccount)
        
        # Create an account with invalid checksum
        invalid_encoded = f"{principal}-invalcrc.{subaccount.hex().lstrip('0')}"
        
        try:
            decodeIcrcAccount(invalid_encoded)
            print(f"✗ Should have rejected invalid checksum: {invalid_encoded}")
            test_count += 1
        except ValueError as e:
            if "Checksum verification failed" in str(e):
                print(f"✓ Correctly rejected invalid checksum")
                test_count += 1
                passed += 1
            else:
                print(f"✗ Wrong error: {str(e)}")
                test_count += 1
    except Exception as e:
        print(f"✗ Test failed unexpectedly: {str(e)}")
        test_count += 1
    
    # Test 5: Invalid account format
    print("\n[TEST] Invalid account format")
    try:
        # Use the predefined invalid formats
        invalid_formats = INVALID_FORMATS
        
        # Count this as a single test with multiple cases
        test_count += 1
        invalid_format_passes = 0
        
        for i, invalid in enumerate(invalid_formats):
            try:
                decodeIcrcAccount(invalid)
                print(f"✗ Should have rejected invalid format: {invalid}")
            except (ValueError, Exception) as e:  # Catch any kind of error
                # Both ValueError and principal format errors are acceptable
                print(f"✓ Correctly rejected invalid format: {invalid} (error: {str(e)})")
                invalid_format_passes += 1
        
        # All invalid formats should be rejected
        if invalid_format_passes == len(invalid_formats):
            passed += 1
    except Exception as e:
        print(f"✗ Test failed unexpectedly: {str(e)}")
        test_count += 1
    
    # Test 6: Round-trip with various principals
    print("\n[TEST] Round-trip with various principals")
    try:
        # Use the predefined test principals
        test_principals = TEST_PRINCIPALS
        
        for principal_text in test_principals:
            principal = Principal.from_str(principal_text)
            print(f"\nTesting with principal: {principal_text}")
            
            # Test with default subaccount
            encoded = encodeIcrcAccount(principal)
            decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
            
            assert str(decoded_owner) == str(principal), f"Expected {principal}, got {decoded_owner}"
            assert decoded_subaccount == bytes(32), f"Expected 32 zero bytes, got {decoded_subaccount}"
            print(f"✓ Default subaccount roundtrip successful")
            
            # Test with a random subaccount
            subaccount = create_random_subaccount()
            encoded = encodeIcrcAccount(principal, subaccount)
            decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
            
            assert str(decoded_owner) == str(principal), f"Expected {principal}, got {decoded_owner}"
            assert decoded_subaccount == subaccount, f"Expected {subaccount}, got {decoded_subaccount}"
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