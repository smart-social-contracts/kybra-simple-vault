import traceback
from typing import List, Optional

from kybra import (
    Async,
    Principal,
    nat,
)
from kybra_simple_logging import get_logger

from vault.candid_types import (
    Account,
    GetAccountTransactionsRequest,
    GetAccountTransactionsResponse,
    ICRCIndexer,
)

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
        max_results: Maximum number of transactions to return
        subaccount: Optional subaccount (as a list of bytes)
        start_tx_id: Transaction ID to start retrieving from (for pagination)

    Returns:
        A GetAccountTransactionsResponse object containing balance and transactions
    """
    try:
        indexer = ICRCIndexer(Principal.from_str(canister_id))
        result = yield indexer.get_account_transactions(
            GetAccountTransactionsRequest(
                account=Account(
                    owner=Principal.from_str(owner_principal), subaccount=subaccount
                ),
                start=start_tx_id,
                max_results=max_results,
            )
        )

        if (
            hasattr(result, "Ok")
            and result.Ok is not None
            and isinstance(result.Ok, dict)
            and "Ok" in result.Ok
        ):
            data = result.Ok["Ok"]
            return GetAccountTransactionsResponse(
                balance=data.get("balance", 0),
                transactions=data.get("transactions", []),
                oldest_tx_id=data.get("oldest_tx_id"),
            )

        # Log errors but don't break the flow
        if hasattr(result, "Err") and result.Err is not None:
            logger.debug(f"Error from indexer: {result.Err}")

    except Exception as e:
        logger.error(f"Exception in get_account_transactions: {str(e)}")

    # Default response for all error cases
    return GetAccountTransactionsResponse(balance=0, transactions=[], oldest_tx_id=None)
