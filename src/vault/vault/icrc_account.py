# Query to get account transactions in Oisy's indexer:
# dfx canister call n5wcd-faaaa-aaaar-qaaea-cai get_account_transactions '(record { account = record { owner = principal "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe"; subaccount = null }; max_results = 50 })' --ic

# Query to get balance in Oisy's indexer:
# dfx canister call mxzaz-hqaaa-aaaar-qaada-cai icrc1_balance_of '(record { owner = principal "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe"; subaccount = null })' --ic

from kybra import Principal
import base64
import binascii
import zlib

# Max length for subaccount in hex (32 bytes = 64 hex chars)
MAX_SUBACCOUNT_HEX_LENGTH = 64

def encodeIcrcAccount(owner: Principal, subaccount: bytes = None) -> str:
    """
    Encodes an ICRC-1 account into a string representation.
    Follows the ICRC-1 standard: https://github.com/dfinity/ICRC-1/blob/main/standards/ICRC-1/TextualEncoding.md
    
    Args:
        owner: The Principal ID of the account owner
        subaccount: Optional 32-byte subaccount identifier. If None or all zeros, defaults to main account.
    
    Returns:
        String representation of the account
    """
    # If subaccount is None or all zeros, just return the principal text
    if subaccount is None or len(subaccount) == 0 or (len(subaccount) == 32 and all(b == 0 for b in subaccount)):
        return str(owner)
    
    # Convert subaccount to hex and remove leading zeros
    subaccount_hex = subaccount.hex()
    subaccount_hex = subaccount_hex.lstrip('0')
    
    # If after removing leading zeros it's empty, it was all zeros
    if not subaccount_hex:
        return str(owner)
    
    # Compute CRC32 checksum for verification
    checksum = compute_crc(owner, subaccount)
    
    # Return formatted account string
    return f"{str(owner)}-{checksum}.{subaccount_hex}"

def compute_crc(owner: Principal, subaccount: bytes) -> str:
    """
    Computes the CRC32 checksum for an ICRC account.
    Matches the TypeScript implementation from @dfinity/utils.
    """
    # Use the canonical bytes attribute for kybra.Principal
    owner_bytes = owner.bytes
    combined = owner_bytes + subaccount
    crc = zlib.crc32(combined)
    checksum_bytes = crc.to_bytes(4, 'big')
    checksum_base32 = base64.b32encode(checksum_bytes).decode('utf-8').lower().rstrip("=")
    return checksum_base32

def decodeIcrcAccount(text: str) -> tuple[Principal, bytes]:
    """
    Decodes an ICRC-1 account string representation.
    
    Args:
        text: The encoded account string
    
    Returns:
        Tuple of (owner_principal, subaccount)
    """
    if not text:
        raise ValueError("Invalid account. No string provided.")
    
    # Check if this is just a principal (main account)
    if "." not in text:
        return Principal.from_str(text), bytes(32)  # Return 32 zero bytes for default subaccount
    
    # Split into principal+checksum and subaccount parts
    principal_and_checksum, subaccount_hex = text.split(".", 1)
    
    # Must have a checksum part
    if "-" not in principal_and_checksum:
        raise ValueError("Invalid account format. Missing checksum.")
    
    # Split principal and checksum
    principal_text, checksum = principal_and_checksum.rsplit("-", 1)
    
    # Create owner principal
    owner = Principal.from_str(principal_text)
    
    # Convert hex subaccount to bytes, padding to 32 bytes
    subaccount = bytes.fromhex(subaccount_hex.zfill(MAX_SUBACCOUNT_HEX_LENGTH))
    
    # Verify checksum
    expected_checksum = compute_crc(owner, subaccount)
    if expected_checksum != checksum:
        raise ValueError("Invalid account. Checksum verification failed.")
    
    return owner, subaccount
