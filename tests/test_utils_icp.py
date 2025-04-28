"""Tests for ICRC account encoding and decoding functions in utils_icp."""

import os
import sys

# Add the parent directory to sys.path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vault.vault.utils_icp import encodeIcrcAccount, decodeIcrcAccount, compute_crc
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
        # Create a test principal
        principal = Principal.from_str("2vxsx-fae")
        
        # Create a test subaccount with a pattern of bytes
        subaccount = bytes(range(1, 33))  # bytes from 1-32
        
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
        principal = Principal.from_str("2vxsx-fae")
        
        # Create a subaccount with leading zeros
        subaccount = bytes([0, 0, 0, 0, 1, 2, 3, 4]) + bytes(24)
        
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
        principal = Principal.from_str("2vxsx-fae")
        subaccount = bytes(range(1, 33))
        
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
        invalid_formats = [
            "",  # Empty string
            "not-a-valid-account",  # Invalid principal
            "2vxsx-fae-checksumonly",  # Missing dot and subaccount
            "2vxsx-fae.",  # Missing subaccount after dot
            ".01020304",  # Missing principal
        ]
        
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
            assert decoded_subaccount == bytes(32), f"Expected 32 zero bytes, got {decoded_subaccount}"
            print(f"✓ Default subaccount roundtrip successful")
            
            # Test with non-default subaccount
            subaccount = bytes([principal_text.encode()[0] % 255]) + os.urandom(31)
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