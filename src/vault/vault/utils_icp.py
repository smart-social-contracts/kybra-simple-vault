# Query to get account transactions in Oisy's indexer:
# dfx canister call n5wcd-faaaa-aaaar-qaaea-cai get_account_transactions '(record { account = record { owner = principal "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe"; subaccount = null }; max_results = 50 })' --ic

# Query to get balance in Oisy's indexer:
# dfx canister call mxzaz-hqaaa-aaaar-qaada-cai icrc1_balance_of '(record { owner = principal "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe"; subaccount = null })' --ic

from kybra import Principal, query, ic
import base64
import binascii
import zlib


def encodeIcrcAccount(owner: Principal, subaccount: bytes = b"") -> str:
    if not subaccount or subaccount == b"\x00" * 32:
        # No subaccount: just return the principal text
        return str(owner)
    else:
        owner_bytes = owner.to_blob()
        combined = owner_bytes + subaccount
        checksum = zlib.crc32(combined)  # Compute CRC-32
        checksum_base32 = base64.b32encode(checksum.to_bytes(4, 'big')).decode('utf-8').lower().rstrip("=")
        subaccount_hex = subaccount.lstrip(b'\x00').hex()
        return f"{str(owner)}-{checksum_base32}.{subaccount_hex}"

def decodeIcrcAccount(text: str) -> tuple[Principal, bytes]:
    if "-" not in text:
        # Simple case: no subaccount
        return Principal.from_str(text), b"\x00" * 32

    owner_text, rest = text.split("-", 1)
    if "." not in rest:
        raise ValueError("Invalid format: no subaccount hex part.")

    checksum_b32, subaccount_hex = rest.split(".", 1)
    checksum = int.from_bytes(base64.b32decode(checksum_b32.upper() + "===="), 'big')
    subaccount_partial = bytes.fromhex(subaccount_hex)

    if subaccount_partial[0] == 0x00:
        raise ValueError("Invalid subaccount: leading zero.")

    subaccount = (b"\x00" * (32 - len(subaccount_partial))) + subaccount_partial

    owner = Principal.from_str(owner_text)
    owner_bytes = owner.to_blob()

    computed_checksum = zlib.crc32(owner_bytes + subaccount)
    if computed_checksum != checksum:
        raise ValueError("Checksum mismatch.")

    return owner, subaccount
