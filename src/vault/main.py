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


# @update
# def do_transfer(to: Principal, amount: nat) -> Async[nat]:
#     from vault.entities import ledger_canister

#     principal = ledger_canister().principal
#     ledger = ICRCLedger(Principal.from_str(principal))

#     args: TransferArg = TransferArg(
#         to=Account(owner=to, subaccount=None),
#         amount=amount,
#         fee=None,  # Optional fee, will use default
#         memo=None,  # Optional memo field
#         from_subaccount=None,  # No subaccount specified
#         created_at_time=None,  # System will use current time
#     )

#     logger.debug(f"Transferring {amount} tokens to {to.to_str()}")
#     result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

#     # Return the transaction id on success or -1 on error
#     return match(
#         result,
#         {
#             "Ok": lambda result_variant: match(
#                 result_variant,
#                 {
#                     "Ok": lambda tx_id: tx_id,  # Return the transaction ID directly
#                     "Err": lambda _: -1,  # Return -1 on transfer error
#                 },
#             ),
#             "Err": lambda _: -1,  # Return -1 on call error
#         },
#     )


# ---- Candid Type Definitions ----



# class Account(Record):
#     owner: Principal
#     subaccount: Opt[Vec[nat8]]  # 32 bytes or None


# class Transfer(Record):
#     from_: Account
#     to: Account
#     amount: nat
#     fee: Opt[nat]
#     memo: Opt[Vec[nat8]]
#     created_at_time: Opt[nat64]
#     spender: Opt[Account]


# class Transaction(Record):
#     burn: Opt[null]
#     kind: str
#     mint: Opt[null]
#     approve: Opt[null]
#     timestamp: nat64
#     transfer: Opt[Transfer]


# class AccountTransaction(Record):
#     id: nat
#     transaction: Transaction


# class GetAccountTransactionsRequest(Record):
#     account: Account
#     max_results: nat


# class GetAccountTransactionsResponse(Record):
#     balance: nat
#     transactions: Vec[AccountTransaction]
#     oldest_tx_id: Opt[nat]
#     # Add other fields as needed


# class GetTransactionsResult(Variant):
#     Ok: GetAccountTransactionsResponse
#     Err: str


# class ICRCIndexer(Service):
#     @service_query
#     def get_account_transactions(
#         self, request: GetAccountTransactionsRequest
#     ) -> Async[GetTransactionsResult]:
#         ...

#     # @service_query
#     # def icrc1_fee(self) -> nat: ...

#     # @service_update
#     # def icrc1_transfer(self, args: TransferArg) -> TransferResult: ...

#     # @service_query
#     # def get_transactions(
#     #     self, request: GetTransactionsRequest
#     # ) -> Async[GetTransactionsResponse]: ...


# @update
# def get_account_transactions_indexer() -> Async[GetAccountTransactionsResponse]:
#     """
#     Query the indexer canister for account transactions, matching the user's dfx example.
#     Returns the CallResult variant (Kybra-compatible).
#     """

#     ic.print("\nQuerying indexer canister for account transactions...")

#     canister_id = "n5wcd-faaaa-aaaar-qaaea-cai"
#     owner_principal = "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe"
#     subaccount = None
#     max_results = 5

#     account = Account(
#         owner=Principal.from_str(owner_principal),
#         subaccount=subaccount if subaccount else None,
#     )
#     req = GetAccountTransactionsRequest(
#         account=account,
#         max_results=max_results,
#     )

#     try:
#         indexer = ICRCIndexer(Principal.from_str(canister_id))
#         result = yield indexer.get_account_transactions(req)
        
#         ic.print(f"Got result type: {type(result)}")
        
#         # Now result is a CallResult with Ok/Err fields
#         if hasattr(result, 'Ok') and result.Ok is not None:
#             # Here the Ok field is a dictionary, not an object
#             ok_data = result.Ok
#             ic.print(f"Result.Ok content: {ok_data}")
            
#             # The actual data is nested inside ok_data['Ok']
#             if isinstance(ok_data, dict) and 'Ok' in ok_data:
#                 transaction_data = ok_data['Ok']
                
#                 # Extract the balance, transactions and oldest_tx_id from the inner dictionary
#                 balance = transaction_data.get('balance', 0)
#                 transactions = transaction_data.get('transactions', [])
#                 oldest_tx_id = transaction_data.get('oldest_tx_id')
                
#                 ic.print(f"Successfully retrieved transactions with balance: {balance}")
                
#                 # Build our response object with the extracted values
#                 return GetAccountTransactionsResponse(
#                     balance=balance,
#                     transactions=transactions,
#                     oldest_tx_id=oldest_tx_id,
#                 )
#             else:
#                 ic.print(f"Ok data doesn't have the expected 'Ok' nested structure: {ok_data}")
#         elif hasattr(result, 'Err') and result.Err is not None:
#             ic.print(f"Error from indexer: {result.Err}")
#         else:
#             ic.print(f"Unexpected result structure: {result}")
        
#         # Default response in error cases
#         ic.print("Returning default response in error cases")
#         return GetAccountTransactionsResponse(
#             balance=0,
#             transactions=[],
#             oldest_tx_id=None,
#         )
#     except Exception as e:
#         ic.print(f"Exception occurred: {str(e)}")
#         return GetAccountTransactionsResponse(
#             balance=0,
#             transactions=[],
#             oldest_tx_id=None,
#         )


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
    
    if not response or not hasattr(response, "transactions") or not response.transactions:
        return f"No transactions found for principal {principal_id}"
    
    # Track new and updated transactions
    new_count = 0
    updated_count = 0
    
    # Process each transaction and update the database
    for tx in response.transactions:
        tx_id = str(tx.id)
        transaction = tx.transaction
        
        # Skip if the transaction doesn't have a transfer
        if not hasattr(transaction, "transfer") or not transaction.transfer:
            continue
            
        transfer = transaction.transfer
        
        # Get principals for from and to accounts
        principal_from = str(transfer.from_.owner) if hasattr(transfer, "from_") and hasattr(transfer.from_, "owner") else "unknown"
        principal_to = str(transfer.to.owner) if hasattr(transfer, "to") and hasattr(transfer.to, "owner") else "unknown"
        
        # Get amount and timestamp
        amount = int(transfer.amount) if hasattr(transfer, "amount") else 0
        timestamp = int(transaction.timestamp) if hasattr(transaction, "timestamp") else 0
        
        # Create or update the VaultTransaction
        existing_tx = VaultTransaction.get(tx_id)
        if existing_tx:
            # Update existing transaction if needed
            if (
                existing_tx.principal_from != principal_from or
                existing_tx.principal_to != principal_to or
                existing_tx.amount != amount or
                existing_tx.timestamp != timestamp or
                existing_tx.kind != transaction.kind
            ):
                existing_tx.principal_from = principal_from
                existing_tx.principal_to = principal_to
                existing_tx.amount = amount
                existing_tx.timestamp = timestamp
                existing_tx.kind = transaction.kind
                existing_tx.save()
                updated_count += 1
        else:
            # Create new transaction
            VaultTransaction(
                _id=tx_id,
                principal_from=principal_from,
                principal_to=principal_to,
                amount=amount,
                timestamp=timestamp,
                kind=transaction.kind
            ).save()
            new_count += 1
    
    result = f"Processed {len(response.transactions)} transactions: {new_count} new, {updated_count} updated"
    ic.print(result)
    return result
