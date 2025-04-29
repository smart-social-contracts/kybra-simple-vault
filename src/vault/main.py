from kybra import (
    Async,
    CallResult,
    Principal,
    StableBTreeMap,
    ic,
    match,
    nat,
    query,
    update,
    void,
    Record,
    Opt,
    ic,
    nat,
    nat64,
    nat8,
    null,
    Opt,
    Vec,
    Record,
    Variant,
    Service,
    service_query,
    service_update,
)
from typing import Optional, List
from kybra_simple_db import *
from kybra_simple_logging import get_logger, set_log_level, Level

# import vault.admin as admin
# import vault.services as services
# import vault.utils_icp as utils_icp
# import vault.utils_neural as utils_neural
from vault.ic_util_calls import get_account_transactions
from vault.entities import VaultTransaction

# import vault.candid_types as candid_types
# from vault.constants import CKBTC_CANISTER, DO_NOT_IMPLEMENT_HEARTBEAT
# from vault.entities import app_data, stats


logger = get_logger(__name__)
set_log_level(Level.DEBUG)


db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100_000, max_value_size=1_000_000
)
db_audit = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100_000, max_value_size=1_000_000
)

Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)

# if not app_data().vault_principal:
#     app_data().vault_principal = ic.id().to_str()


@update
def do_transfer(to: Principal, amount: nat) -> Async[nat]:
    from vault.entities import ledger_canister

    principal = ledger_canister().principal
    ledger = ICRCLedger(Principal.from_str(principal))

    args: TransferArg = TransferArg(
        to=Account(owner=to, subaccount=None),
        amount=amount,
        fee=None,  # Optional fee, will use default
        memo=None,  # Optional memo field
        from_subaccount=None,  # No subaccount specified
        created_at_time=None,  # System will use current time
    )

    logger.debug(f"Transferring {amount} tokens to {to.to_str()}")
    result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

    # Return the transaction id on success or -1 on error
    return match(
        result,
        {
            "Ok": lambda result_variant: match(
                result_variant,
                {
                    "Ok": lambda tx_id: tx_id,  # Return the transaction ID directly
                    "Err": lambda _: -1,  # Return -1 on transfer error
                },
            ),
            "Err": lambda _: -1,  # Return -1 on call error
        },
    )


@update
def update_transaction_history(principal_id: str) -> str:
    """
    Updates the transaction history for a given principal by querying the ICRC indexer
    and storing the transactions in the VaultTransaction database.
    
    Args:
        principal_id: The principal ID to update transaction history for
        
    Returns:
        A status message indicating the number of transactions processed
    """
    ic.print(f"Updating transaction history for {principal_id}...")
    
    # Default indexer canister for ckBTC
    indexer_canister_id = "n5wcd-faaaa-aaaar-qaaea-cai"
    max_results = 20
    
    # Query the indexer for transactions
    response = yield get_account_transactions(
        canister_id=indexer_canister_id,
        owner_principal=principal_id,
        max_results=max_results
    )
    
    ic.print(f"Response: {response}")
    
    # Check if we have transactions in the response
    has_transactions = 'transactions' in response and response['transactions']
    
    if not response or not has_transactions:
        return f"No transactions found for principal {principal_id}"
    
    # Track new and updated transactions
    new_count = 0
    updated_count = 0
    
    # Process each transaction and update the database
    for tx in response['transactions']:
        # Extract transaction data using dictionary access
        tx_id = str(tx['id'])
        transaction = tx['transaction']
        
        # Skip if the transaction doesn't have a transfer
        if 'transfer' not in transaction or not transaction['transfer']:
            continue
            
        transfer = transaction['transfer']
        
        # Get principals for from and to accounts
        principal_from = str(transfer['from_']['owner']) if 'from_' in transfer and 'owner' in transfer['from_'] else "unknown"
        principal_to = str(transfer['to']['owner']) if 'to' in transfer and 'owner' in transfer['to'] else "unknown"
        
        # Get amount and timestamp
        amount = int(transfer['amount']) if 'amount' in transfer else 0
        timestamp = int(transaction['timestamp']) if 'timestamp' in transaction else 0
        kind = transaction['kind'] if 'kind' in transaction else "unknown"
        
        # Create or update the VaultTransaction
        existing_tx = VaultTransaction[tx_id]
        if existing_tx:
            # Update existing transaction if needed
            if (
                existing_tx.principal_from != principal_from or
                existing_tx.principal_to != principal_to or
                existing_tx.amount != amount or
                existing_tx.timestamp != timestamp or
                existing_tx.kind != kind
            ):
                existing_tx.principal_from = principal_from
                existing_tx.principal_to = principal_to
                existing_tx.amount = amount
                existing_tx.timestamp = timestamp
                existing_tx.kind = kind
                updated_count += 1
        else:
            # Create new transaction
            VaultTransaction(
                _id=tx_id,
                principal_from=principal_from,
                principal_to=principal_to,
                amount=amount,
                timestamp=timestamp,
                kind=kind
            )
            new_count += 1
    
    result = f"Processed {len(response['transactions'])} transactions: {new_count} new, {updated_count} updated"
    ic.print(result)
    return result
