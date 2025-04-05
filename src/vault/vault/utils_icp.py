from kybra import (
    CallResult,
    Principal,
    nat,
    Async,
)

from vault.constants import CKBTC_CANISTER

from vault.candid_types import (
    GetTransactionsRequest,
    ICRCLedger,
    GetTransactionsResponse
)


from kybra_simple_logging import get_logger

logger = get_logger(__name__)
logger.set_level(logger.DEBUG)


def get_transactions(start: nat, length: nat) -> Async[GetTransactionsResponse]:
    logger.debug('Querying for transactions: from %s, give me %s transactions' % (start, length))
    ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))
    request = GetTransactionsRequest(start=start, length=length)
    ret: CallResult[GetTransactionsResponse] = yield ledger.get_transactions(request)
    if ret.Ok:
        logger.debug("Response from get_transactions(%s, %s): %s" % (start, length, ret.Ok))
    if ret.Err:
        logger.error("Error from get_transactions(%s, %s): %s" % (start, length, ret.Err))
    return ret

