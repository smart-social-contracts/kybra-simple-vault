from kybra import (
    Async,
    CallResult,
    Principal,
    Record,
    Variant,
    Vec,
    nat,
    nat64,
    nat8,
    null,
    Opt,
    ic,
    Service,
    service_query,
    service_update,
)
from typing import Optional, List


class Account(Record):
    owner: Principal
    subaccount: Opt[Vec[nat8]]


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


class GetTransactionsResult(Variant):
    Ok: GetAccountTransactionsResponse
    Err: str


# class ICRCIndexer:
#     def __init__(self, principal_id: Principal):
#         self.principal_id = principal_id

#     def get_account_transactions(self, req: GetAccountTransactionsRequest) -> Async[GetTransactionsResult]:
#         from kybra import Service, service_query

#         class IndexerService(Service):
#             @service_query
#             def get_account_transactions(
#                 self, request: GetAccountTransactionsRequest
#             ) -> Async[GetTransactionsResult]: ...

#         indexer = IndexerService(self.principal_id)
#         return indexer.get_account_transactions(req)


class ICRCIndexer(Service):
    @service_query
    def get_account_transactions(
        self, request: GetAccountTransactionsRequest
    ) -> Async[GetTransactionsResult]:
        ...


def get_account_transactions(
    canister_id: str,
    owner_principal: str,
    subaccount: Optional[List[int]] = None,
    max_results: int = 10
) -> Async[GetAccountTransactionsResponse]:
    """
    Query the indexer canister for account transactions.

    Args:
        canister_id: The principal ID of the indexer canister
        owner_principal: The principal ID of the account owner
        subaccount: Optional subaccount (as a list of bytes)
        max_results: Maximum number of transactions to return

    Returns:
        A GetAccountTransactionsResponse object containing balance and transactions
    """
    ic.print(f"\nQuerying indexer canister for account transactions for {owner_principal}...")

    account = Account(
        owner=Principal.from_str(owner_principal),
        subaccount=subaccount if subaccount else None,
    )
    req = GetAccountTransactionsRequest(
        account=account,
        max_results=max_results,
    )

    default_response = GetAccountTransactionsResponse(
        balance=0,
        transactions=[],
        oldest_tx_id=None,
    )

    try:
        indexer = ICRCIndexer(Principal.from_str(canister_id))
        result = yield indexer.get_account_transactions(req)

        ic.print(f"Got result type: {type(result)}")

        # Handle the CallResult with Ok/Err fields
        if hasattr(result, 'Ok') and result.Ok is not None:
            ok_data = result.Ok
            ic.print(f"Result.Ok content: {ok_data}")

            # The actual data is nested inside ok_data['Ok']
            if isinstance(ok_data, dict) and 'Ok' in ok_data:
                transaction_data = ok_data['Ok']

                # Extract the balance, transactions and oldest_tx_id from the inner dictionary
                balance = transaction_data.get('balance', 0)
                transactions = transaction_data.get('transactions', [])
                oldest_tx_id = transaction_data.get('oldest_tx_id')

                ic.print(f"Successfully retrieved {len(transactions)} transactions with balance: {balance}")

                # Build our response object
                return GetAccountTransactionsResponse(
                    balance=balance,
                    transactions=transactions,
                    oldest_tx_id=oldest_tx_id,
                )
            else:
                ic.print(f"Ok data doesn't have the expected 'Ok' nested structure: {ok_data}")
        elif hasattr(result, 'Err') and result.Err is not None:
            ic.print(f"Error from indexer: {result.Err}")
        else:
            ic.print(f"Unexpected result structure: {result}")

        # Default response in error cases
        ic.print("Returning default response in error cases")
        return default_response
    except Exception as e:
        ic.print(f"Exception occurred: {str(e)}")
        return default_response


def get_account_transactions_indexer(
    canister_id: str,
    owner_principal: str,
    subaccount: Optional[List[int]] = None,
    max_results: int = 10
) -> GetAccountTransactionsResponse:
    """
    Query the indexer canister for account transactions.

    Args:
        canister_id: The principal ID of the indexer canister
        owner_principal: The principal ID of the account owner
        subaccount: Optional subaccount (as a list of bytes)
        max_results: Maximum number of transactions to return

    Returns:
        A GetAccountTransactionsResponse object containing balance and transactions
    """
    return get_account_transactions(
        canister_id=canister_id,
        owner_principal=owner_principal,
        subaccount=subaccount,
        max_results=max_results,
    )


def get_account_transactions_indexer_for_principal(
    principal_id: str,
    canister_id: str,
    owner_principal: str,
    subaccount: Optional[List[int]] = None,
    max_results: int = 10
) -> GetAccountTransactionsResponse:
    """
    Query the indexer canister for account transactions for a specific principal.

    Args:
        principal_id: The principal ID of the principal
        canister_id: The principal ID of the indexer canister
        owner_principal: The principal ID of the account owner
        subaccount: Optional subaccount (as a list of bytes)
        max_results: Maximum number of transactions to return

    Returns:
        A GetAccountTransactionsResponse object containing balance and transactions
    """
    return get_account_transactions_indexer(
        canister_id=canister_id,
        owner_principal=owner_principal,
        subaccount=subaccount,
        max_results=max_results,
    )
