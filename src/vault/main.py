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
)
from kybra_simple_db import *
from kybra_simple_logging import get_logger, set_log_level

import vault.admin as admin
import vault.services as services
import vault.utils_icp as utils_icp
from vault.candid_types import (
    Account,
    GetTransactionsResponse,
    GetTransactionsResult,
    ICRCLedger,
    TransferArg,
)
from vault.constants import CKBTC_CANISTER, DO_NOT_IMPLEMENT_HEARTBEAT
from vault.entities import app_data, stats

logger = get_logger(__name__)
set_log_level(logger.DEBUG)


db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100_000, max_value_size=1_000_000
)
db_audit = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100_000, max_value_size=1_000_000
)

Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)

if not app_data().vault_principal:
    app_data().vault_principal = ic.id().to_str()


@query
def get_balance() -> Async[Principal]:
    return ic.id()


@update
def get_transactions(start: nat, length: nat) -> Async[GetTransactionsResult]: # TODO: use indexer instead
    ret: CallResult[GetTransactionsResponse] = yield utils_icp.get_transactions(
        start, length
    )
    return match(
        ret,
        {
            "Ok": lambda ok: {"Ok": ok},
            "Err": lambda err: {"Err": str(err)},
        },
    )


@query
def get_canister_balance() -> Async[str]:  # TODO: probably use indexer instead
    ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))
    account = Account(owner=ic.id(), subaccount=None)

    result: CallResult[nat] = yield ledger.icrc1_balance_of(account)

    return match(
        result,
        {
            "Ok": lambda ok: str(ok),
            "Err": lambda err: "-1",  # Return -1 balance on error
        },
    )


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




@query
def get_stats() -> str:
    return str(stats())


@update
def set_admin(principal: Principal) -> str:
    return admin.set_admin(ic.caller().to_str(), principal.to_str())


@update
def reset() -> str:
    return admin.reset(ic.caller().to_str())


@update
def set_ledger_canister(canister_id: str, principal: Principal) -> str:
    return admin.set_ledger_canister(
        ic.caller().to_str(), canister_id, principal.to_str()
    )
