import time
from vault.candid_types import Account, ICRCLedger, TransferArg
from kybra import Principal, ic, update, nat

def run() -> int:
    # Test setup - first deposit some tokens to the canister
    ledger = ICRCLedger(Principal.from_str("ryjl3-tyaaa-aaaaa-aaaba-cai"))  # Local ICRC ledger canister
    
    # Get a test account 
    test_account = Principal.from_str("rwlgt-iiaaa-aaaaa-aaaaa-cai")  # Test account ID
    
    print("Setting up test - minting tokens to the canister...")
    # First mint some tokens to the canister
    mint_result = ledger.icrc1_transfer(TransferArg(
        to=Account(owner=ic.id(), subaccount=None),
        amount=nat(1000_000),  # 1 token assuming 6 decimals
        fee=None,
        memo=None,
        from_subaccount=None,
        created_at_time=None
    ))
    
    # Give some time for the mint to process
    time.sleep(2)
    
    print("Getting initial balance...")
    initial_balance = get_canister_balance()
    print(f"Initial balance: {initial_balance}")
    
    # Test sending tokens
    print("Testing send...")
    transfer_result = ic.call(ic.id(), "do_transfer", (test_account, nat(500_000)))
    
    # Give some time for the transfer to process
    time.sleep(2)
    
    print("Getting final balance...")
    final_balance = get_canister_balance()
    print(f"Final balance: {final_balance}")
    
    # Verify the balance has decreased
    assert int(initial_balance) - int(final_balance) >= 500_000, "Transfer did not decrease balance"
    
    print("Test passed!")
    return 0

# Helper function to query the canister's balance
def get_canister_balance() -> str:
    # Call the canister's get_canister_balance function directly
    return ic.call(ic.id(), "get_canister_balance", ())
