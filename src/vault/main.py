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
# from kybra_simple_db import *
# from kybra_simple_logging import get_logger, set_log_level, Level

# import vault.admin as admin
# import vault.services as services
# import vault.utils_icp as utils_icp
# from vault.candid_types import (
#     Account,
#     GetTransactionsResponse,
#     GetTransactionsResult,
#     ICRCLedger,
#     TransferArg,
# )
# from vault.constants import CKBTC_CANISTER, DO_NOT_IMPLEMENT_HEARTBEAT
# from vault.entities import app_data, stats


# logger = get_logger(__name__)
# set_log_level(Level.DEBUG)


# db_storage = StableBTreeMap[str, str](
#     memory_id=0, max_key_size=100_000, max_value_size=1_000_000
# )
# db_audit = StableBTreeMap[str, str](
#     memory_id=1, max_key_size=100_000, max_value_size=1_000_000
# )

# Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)

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

class Account(Record):
    owner: Principal
    subaccount: Opt[Vec[nat8]]  # 32 bytes or None


class Transfer(Record):
    from_: Account
    to: Account
    amount: nat
    fee: Opt[nat]
    memo: Opt[Vec[nat8]]
    created_at_time: Opt[nat64]
    spender: Opt[Account]


class Transaction(Record):
    burn: Opt[null]
    kind: str
    mint: Opt[null]
    approve: Opt[null]
    timestamp: nat64
    transfer: Opt[Transfer]


class AccountTransaction(Record):
    id: nat
    transaction: Transaction


class GetAccountTransactionsRequest(Record):
    account: Account
    max_results: nat


class GetAccountTransactionsResponse(Record):
    balance: nat
    transactions: Vec[AccountTransaction]
    oldest_tx_id: Opt[nat]
    # Add other fields as needed


class ICRCIndexer(Service):
    @service_query
    def get_account_transactions(
        self, request: GetAccountTransactionsRequest
    ) -> Async[GetAccountTransactionsResponse]:
        ...

    # @service_query
    # def icrc1_balance_of(self, account: Account) -> nat: ...

    # @service_query
    # def icrc1_fee(self) -> nat: ...

    # @service_update
    # def icrc1_transfer(self, args: TransferArg) -> TransferResult: ...

    # @service_query
    # def get_transactions(
    #     self, request: GetTransactionsRequest
    # ) -> Async[GetTransactionsResponse]: ...


@update
def get_account_transactions_indexer() -> Async[GetAccountTransactionsResponse]:
    """
    Query the indexer canister for account transactions, matching the user's dfx example.
    Returns the CallResult variant (Kybra-compatible).
    """

    ic.print("\nQuerying indexer canister for account transactions...")

    canister_id = "n5wcd-faaaa-aaaar-qaaea-cai"
    owner_principal = "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe"
    subaccount = None
    max_results = 5

    account = Account(
        owner=Principal.from_str(owner_principal),
        subaccount=subaccount if subaccount else None,
    )
    req = GetAccountTransactionsRequest(
        account=account,
        max_results=max_results,
    )

    try:
        indexer = ICRCIndexer(Principal.from_str(canister_id))
        result = yield indexer.get_account_transactions(req)
        
        # Handle potential None values
        if result is None:
            ic.print("Service call failed with None result")
            return GetAccountTransactionsResponse(
                balance=0,
                transactions=[],
                oldest_tx_id=None,
            )
        
        # Check if we have an Ok value
        if hasattr(result, 'Ok') and result.Ok is not None:
            ic.print(f"Successfully retrieved transactions: {result.Ok}")
            return result.Ok
        elif hasattr(result, 'Err') and result.Err is not None:
            ic.print(f"Error from indexer: {result.Err}")
        else:
            ic.print(f"Unexpected result structure: {result}")
        
        ic.print("Returning default response in error cases")
        # Default response in error cases
        return GetAccountTransactionsResponse(
            balance=0,
            transactions=[],
            oldest_tx_id=None,
        )
    except Exception as e:
        ic.print(f"Exception occurred: {str(e)}")
        return GetAccountTransactionsResponse(
            balance=0,
            transactions=[],
            oldest_tx_id=None,
        )
