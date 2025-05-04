import traceback
from typing import List, Optional

from kybra import (
    Async,
    Principal,
    nat,
)

from vault.candid_types import (
    Account,
    GetAccountTransactionsRequest,
    GetAccountTransactionsResponse,
    ICRCIndexer,
)

from kybra_simple_logging import get_logger

logger = get_logger(__name__)


def get_account_transactions(
    canister_id: str,
    owner_principal: str,
    max_results: nat,
    subaccount: Optional[List[int]] = None,
    start_tx_id: Optional[nat] = 0,
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

    # start_tx_id = 0 if start_tx_id is None else start_tx_id
    logger.debug(f"\nQuerying indexer canister for account transactions for {owner_principal} starting from tx id {start_tx_id}...")

    account = Account(
        owner=Principal.from_str(owner_principal),
        subaccount=subaccount if subaccount else None,
    )
    req = GetAccountTransactionsRequest(
        account=account,
        start=start_tx_id,
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

        logger.debug(f"Result: {result}")

        # Handle the CallResult with Ok/Err fields
        if hasattr(result, "Ok") and result.Ok is not None:
            ok_data = result.Ok
            logger.debug(f"Result.Ok content: {ok_data}")

            # The actual data is nested inside ok_data['Ok']
            if isinstance(ok_data, dict) and "Ok" in ok_data:
                transaction_data = ok_data["Ok"]
                logger.debug(f"Transaction data: {transaction_data}")

                # Extract the balance, transactions and oldest_tx_id from the inner dictionary
                balance = transaction_data.get("balance", 0)
                transactions = transaction_data.get("transactions", [])
                oldest_tx_id = transaction_data.get("oldest_tx_id")

                logger.debug(
                    f"Successfully retrieved {len(transactions)} transactions and total principal balance of {balance}"
                )
                logger.debug(f"Oldest tx id: {oldest_tx_id}")
                logger.debug(f"Transactions: {transactions}")
                logger.debug(f"Balance: {balance}")

                # Build our response object
                return GetAccountTransactionsResponse(
                    balance=balance,
                    transactions=transactions,
                    oldest_tx_id=oldest_tx_id,
                )
            else:
                logger.debug(
                    f"Ok data doesn't have the expected 'Ok' nested structure: {ok_data}"
                )
        elif hasattr(result, "Err") and result.Err is not None:
            logger.debug(f"Error from indexer: {result.Err}")
        else:
            logger.debug(f"Unexpected result structure: {result}")

        # Default response in error cases
        logger.debug("Returning default response in error cases")
        return default_response
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}\n{traceback.format_exc()}")
        return default_response

