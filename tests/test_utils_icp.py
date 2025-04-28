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
    "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae",  # Principal from TS example
    "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe",  # Long principal
    "aaaaa-aa"                                                          # IC management canister
]

# Create different patterns of subaccounts for testing
DEFAULT_SUBACCOUNT = bytes(32)  # 32 zeros
SEQUENTIAL_SUBACCOUNT = bytes(range(1, 33))  # bytes 1 through 32 (same as TS example)
LEADING_ZEROS_SUBACCOUNT = bytes([0, 0, 0, 0, 1, 2, 3, 4]) + bytes(24)  # Leading zeros followed by pattern

# Hardcoded expected account IDs based on the implementation
EXPECTED_ACCOUNT_IDS = {
    # Principal-only accounts (no subaccount)
    "principal_short": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae",
    "principal_long": "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe",
    "principal_ic": "aaaaa-aa",
    
    # With sequential subaccount (1-32)
    "sequential_short": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae-dfxgiyy.102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20",
    "sequential_long": "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe-635b25y.102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20", 
    "sequential_ic": "aaaaa-aa-ejfzjpi.102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20",
    
    # With leading zeros subaccount
    "leading_zeros_short": "k2t6j-2nvnp-4zjm3-25dtz-6xhaa-c7boj-5gayf-oj3xs-i43lp-teztq-6ae-owbgcnq.1020304000000000000000000000000000000000000000000000000",
    "leading_zeros_long": "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe-xvi4qyy.1020304000000000000000000000000000000000000000000000000",
    "leading_zeros_ic": "aaaaa-aa-nhqedki.1020304000000000000000000000000000000000000000000000000"
}

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
        # Test all principal types with default subaccount
        for i, principal_text in enumerate(TEST_PRINCIPALS):
            principal = Principal.from_str(principal_text)
            expected_account_id = principal_text  # Default subaccount should just be the principal
            
            # Encode with default subaccount (None)
            encoded1 = encodeIcrcAccount(principal)
            assert encoded1 == expected_account_id, f"Expected {expected_account_id}, got {encoded1}"
            print(f"✓ Principal {i+1}: {principal_text} -> {encoded1}")
            
            # Encode with empty subaccount
            encoded2 = encodeIcrcAccount(principal, bytes(0))
            assert encoded2 == expected_account_id, f"Expected {expected_account_id}, got {encoded2}"
            
            # Encode with zero subaccount
            encoded3 = encodeIcrcAccount(principal, bytes(32))
            assert encoded3 == expected_account_id, f"Expected {expected_account_id}, got {encoded3}"
            
            # Decode the account ID
            decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded1)
            
            # Verify owner
            assert str(decoded_owner) == principal_text, f"Expected {principal_text}, got {decoded_owner}"
            
            # Verify subaccount (should be all zeros)
            assert decoded_subaccount == bytes(32), f"Expected 32 zero bytes, got {decoded_subaccount}"
            
        print(f"✓ All default subaccount encodings verified against expected values")
        
        test_count += 1
        passed += 1
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        test_count += 1
    
    # Test 2: Specific subaccount encoding with sequential pattern
    print("\n[TEST] Specific subaccount encoding with sequential pattern")
    try:
        # Test all principals with sequential subaccount
        for i, principal_text in enumerate(TEST_PRINCIPALS):
            principal = Principal.from_str(principal_text)
            subaccount = SEQUENTIAL_SUBACCOUNT
            
            # Get the expected account ID from our precomputed values
            if i == 0:
                expected_account_id = EXPECTED_ACCOUNT_IDS["sequential_short"]
            elif i == 1:
                expected_account_id = EXPECTED_ACCOUNT_IDS["sequential_long"]
            else:
                expected_account_id = EXPECTED_ACCOUNT_IDS["sequential_ic"]
            
            # Encode the account
            encoded = encodeIcrcAccount(principal, subaccount)
            
            # Verify against expected account ID
            assert encoded == expected_account_id, f"Expected {expected_account_id}, got {encoded}"
            print(f"✓ Principal {i+1} with sequential subaccount: {encoded}")
            
            # Additional format checks
            assert "-" in encoded, f"Expected hyphen in {encoded}"
            assert "." in encoded, f"Expected period in {encoded}"
            
            # Decode to verify owner and subaccount
            decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
            assert str(decoded_owner) == principal_text, f"Expected owner {principal_text}, got {decoded_owner}"
            assert decoded_subaccount == subaccount, f"Subaccount mismatch"
            
        print(f"✓ All sequential subaccount encodings verified against expected values")
        
        test_count += 1
        passed += 1
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        test_count += 1
    
    # Test 3: Leading zeros in subaccount
    print("\n[TEST] Leading zeros in subaccount")
    try:
        # Test all principals with leading zeros subaccount
        for i, principal_text in enumerate(TEST_PRINCIPALS):
            principal = Principal.from_str(principal_text)
            subaccount = LEADING_ZEROS_SUBACCOUNT
            
            # Get the expected account ID from our precomputed values
            if i == 0:
                expected_account_id = EXPECTED_ACCOUNT_IDS["leading_zeros_short"]
            elif i == 1:
                expected_account_id = EXPECTED_ACCOUNT_IDS["leading_zeros_long"]
            else:
                expected_account_id = EXPECTED_ACCOUNT_IDS["leading_zeros_ic"]
            
            # Encode the account
            encoded = encodeIcrcAccount(principal, subaccount)
            
            # Verify against expected account ID
            assert encoded == expected_account_id, f"Expected {expected_account_id}, got {encoded}"
            print(f"✓ Principal {i+1} with leading zeros: {encoded}")
            
            # Verify format
            parts = encoded.split(".")
            assert len(parts) == 2, f"Expected format with dot separator, got {encoded}"
            
            # Subaccount hex part should not have leading zeros
            subaccount_hex = parts[1]
            assert not subaccount_hex.startswith("0"), f"Should not have leading zeros: {subaccount_hex}"
            
            # Decode and verify subaccount
            decoded_owner, decoded_subaccount = decodeIcrcAccount(encoded)
            assert decoded_subaccount == subaccount, f"Subaccount mismatch"
        
        print(f"✓ All leading zeros subaccount encodings verified against expected values")
        
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
    
    # Test 6: Completeness test with all expected IDs
    print("\n[TEST] Completeness test with all expected IDs")
    try:
        # Test all expected account IDs
        for key, expected_account_id in EXPECTED_ACCOUNT_IDS.items():
            print(f"Testing {key}: {expected_account_id[:20]}... ")
            
            # Determine which subaccount to use based on the key
            if key.startswith("principal_"):
                # For principal-only keys, we use default subaccount
                if key == "principal_short":
                    principal = Principal.from_str(TEST_PRINCIPALS[0])
                    subaccount = None
                elif key == "principal_long":
                    principal = Principal.from_str(TEST_PRINCIPALS[1])
                    subaccount = None
                else:  # principal_ic
                    principal = Principal.from_str(TEST_PRINCIPALS[2])
                    subaccount = None
            elif key.startswith("sequential_"):
                # For sequential subaccount keys
                if key == "sequential_short":
                    principal = Principal.from_str(TEST_PRINCIPALS[0])
                    subaccount = SEQUENTIAL_SUBACCOUNT
                elif key == "sequential_long":
                    principal = Principal.from_str(TEST_PRINCIPALS[1])
                    subaccount = SEQUENTIAL_SUBACCOUNT
                else:  # sequential_ic
                    principal = Principal.from_str(TEST_PRINCIPALS[2])
                    subaccount = SEQUENTIAL_SUBACCOUNT
            elif key.startswith("leading_zeros_"):
                # For leading zeros subaccount keys
                if key == "leading_zeros_short":
                    principal = Principal.from_str(TEST_PRINCIPALS[0])
                    subaccount = LEADING_ZEROS_SUBACCOUNT
                elif key == "leading_zeros_long":
                    principal = Principal.from_str(TEST_PRINCIPALS[1])
                    subaccount = LEADING_ZEROS_SUBACCOUNT
                else:  # leading_zeros_ic
                    principal = Principal.from_str(TEST_PRINCIPALS[2])
                    subaccount = LEADING_ZEROS_SUBACCOUNT
            
            # Encode with the specified principal and subaccount
            encoded = encodeIcrcAccount(principal, subaccount)
            
            # Verify against the expected account ID
            assert encoded == expected_account_id, f"Expected {expected_account_id}, got {encoded}"
            print(f"✓ Encoded correctly: {encoded[:20]}...")
            
            # Also verify decoding
            decoded_owner, decoded_subaccount = decodeIcrcAccount(expected_account_id)
            principal_str = str(principal)
            assert str(decoded_owner) == principal_str, f"Expected {principal_str}, got {decoded_owner}"
            print(f"✓ Decoded owner correctly: {decoded_owner}")
            
            # Verify subaccount if present
            if subaccount is not None:
                assert decoded_subaccount == subaccount, f"Subaccount mismatch"
                print(f"✓ Decoded subaccount correctly")
            else:
                assert decoded_subaccount == bytes(32), f"Expected default subaccount"
                print(f"✓ Decoded default subaccount correctly")
        
        print(f"\n✓ All expected account IDs verified successfully")
        
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