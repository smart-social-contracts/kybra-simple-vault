from kybra import (
    Async,
    CallResult,
    Principal,
    nat,
)
from kybra_simple_logging import get_logger

from vault.candid_types import (
    GetTransactionsRequest,
    GetTransactionsResponse,
    ICRCLedger,
)
from vault.entities import LedgerCanister

logger = get_logger(__name__)
logger.set_level(logger.DEBUG)


def get_transactions(start: nat, length: nat) -> Async[GetTransactionsResponse]:
    principal = LedgerCanister["ckBTC"].principal

    logger.debug(
        "Querying for transactions on ckBTC ledger with principal %s: from %s, give me %s transactions"
        % (principal, start, length)
    )

    ledger = ICRCLedger(Principal.from_str(principal))
    request = GetTransactionsRequest(start=start, length=length)
    ret: CallResult[GetTransactionsResponse] = yield ledger.get_transactions(request)
    if ret.Ok:
        logger.debug(
            "Response from get_transactions(%s, %s): %s" % (start, length, ret.Ok)
        )
    if ret.Err:
        logger.error(
            "Error from get_transactions(%s, %s): %s" % (start, length, ret.Err)
        )
    return ret
