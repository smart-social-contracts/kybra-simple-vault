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
    # First try to get the principal from LedgerCanister
    principal = None
    try:
        principal = LedgerCanister["ckBTC"].principal
        if principal:
            logger.debug(f"Using principal from LedgerCanister: {principal}")
    except (KeyError, AttributeError, IndexError) as e:
        logger.warning(f"Error accessing LedgerCanister principal: {e}")
        
    # If that fails, try to get it from app_data
    if not principal:
        from vault.entities import app_data
        try:
            data = app_data()
            if hasattr(data, 'ledger_canister_principal') and data.ledger_canister_principal:
                principal = data.ledger_canister_principal
                logger.debug(f"Using principal from app_data: {principal}")
        except Exception as e:
            logger.warning(f"Error accessing app_data().ledger_canister_principal: {e}")
    
    # If we still don't have a principal, fall back to constant
    if not principal:
        from vault.constants import MAINNET_CKBTC_LEDGER_PRINCIPAL
        principal = MAINNET_CKBTC_LEDGER_PRINCIPAL
        logger.warning(f"No principal found, falling back to MAINNET_CKBTC_LEDGER_PRINCIPAL: {principal}")
        
        # Store this for future use
        try:
            from vault.entities import app_data
            data = app_data()
            data.ledger_canister_principal = principal
            logger.info(f"Stored fallback principal in app_data: {principal}")
        except Exception as e:
            logger.error(f"Failed to store fallback principal in app_data: {e}")
        
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
