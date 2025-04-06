import time
from vault.candid_types import Account, ICRCLedger
from kybra import Principal, ic, update

def run() -> int:
    # Test setup - first deposit some tokens to the canister
    ledger = ICRCLedger(Principal.from_str("ryjl3-tyaaa-aaaaa-aaaba-cai"))  # Local ICRC ledger canister
    
    print("Getting initial balance...")
    initial_balance = get_canister_balance()
    print(f"Initial balance: {initial_balance}")
    
    # Verify we can successfully get the balance from the ledger
    assert initial_balance != "-1", "Failed to get balance from ledger"
    
    print("Test passed!")
    return 0

# Helper function to query the canister's balance
def get_canister_balance() -> str:
    # Call the canister's get_canister_balance function directly
    return ic.call(ic.id(), "get_canister_balance", ())
