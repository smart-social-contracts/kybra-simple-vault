import utils_icp
from kybra import (
    Async,
    CallResult,
    Principal,
    StableBTreeMap,
    heartbeat,
    ic,
    match,
    nat,
    query,
    update,
    void,
)
from kybra_simple_db import *  # TODO
from kybra_simple_logging import get_logger, set_log_level

import vault.services as services
from vault.candid_types import (
    Account,
    GetTransactionsRequest,
    GetTransactionsResponse,
    GetTransactionsResult,
    ICRCLedger,
    TransferArg,
)
from vault.constants import CKBTC_CANISTER, DO_NOT_IMPLEMENT_HEARTBEAT
from vault.entities import Balance, VaultTransaction, app_data

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


heartbeat_interval_seconds = app_data().heartbeat_interval_seconds

if not DO_NOT_IMPLEMENT_HEARTBEAT:

    @heartbeat
    def heartbeat_() -> Async[void]:
        if (
            heartbeat_interval_seconds
            and ic.time() - app_data().last_heartbeat_time
            > heartbeat_interval_seconds * 1e9
        ):
            logger.debug("Heartbeat started")
            app_data().last_heartbeat_time = ic.time()
            yield services.TransactionTracker().check_transactions()
            logger.debug("Heartbeat finished")


def _only_if_admin() -> bool:
    admin = app_data().admin_principal
    if admin and admin != ic.caller().to_str():
        raise ValueError(
            f"Caller {ic.caller().to_str()} is not the current admin principal {admin}"
        )


def _stats():
    return {
        "app_data": app_data().to_dict(),
        "balances": [_.to_dict() for _ in Balance.instances()],
        "vault_transactions": [_.to_dict() for _ in VaultTransaction.instances()],
    }


@query
def get_canister_id() -> Async[Principal]:
    return ic.id()


@update
def get_transactions(start: nat, length: nat) -> Async[GetTransactionsResult]:
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
def get_canister_balance() -> Async[str]:
    # TODO: this one doesn't work but it doesn't matter... try with call_raw
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
    ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))

    args: TransferArg = TransferArg(
        to=Account(owner=to, subaccount=None),
        amount=amount,
        fee=None,  # Optional fee, will use default
        memo=None,  # Optional memo field
        from_subaccount=None,  # No subaccount specified
        created_at_time=None,  # System will use current time
    )

    result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

    return match(result, {"Ok": lambda ok: 0, "Err": lambda err: -1})


@update
def check_transactions() -> Async[str]:
    ret = yield services.TransactionTracker().check_transactions()
    return str(ret)


@query
def stats() -> str:
    return str(_stats())


@update
def set_admin(principal: Principal) -> str:
    _only_if_admin()
    logger.info(
        f"Setting admin from {app_data().admin_principal} to {principal.to_str()}"
    )
    app_data().admin_principal = principal.to_str()
    return str(_stats())


if not DO_NOT_IMPLEMENT_HEARTBEAT:

    @update
    def set_heartbeat_interval_seconds(seconds: nat) -> str:
        _only_if_admin()
        global heartbeat_interval_seconds
        heartbeat_interval_seconds = seconds
        app_data().heartbeat_interval_seconds = seconds
        return str(_stats())


@update
def reset() -> str:
    _only_if_admin()
    services.reset()
    return str(_stats())


#################
# TODO: remove in production


@query
def version() -> str:
    return "0.7.4"


@update
def execute_code(code: str) -> str:
    """Executes Python code and returns the output.

    This is the core function needed for the Kybra Simple Shell to work.
    It captures stdout, stderr, and return values from the executed code.
    """
    import io
    import sys
    import traceback

    stdout = io.StringIO()
    stderr = io.StringIO()
    sys.stdout = stdout
    sys.stderr = stderr

    try:
        # Try to evaluate as an expression
        result = eval(code, globals())
        if result is not None:
            print(repr(result))
    except SyntaxError:
        try:
            # If it's not an expression, execute it as a statement
            # Use the built-in exec function but with a different name to avoid conflict
            exec_builtin = exec
            exec_builtin(code, globals())
        except Exception:
            traceback.print_exc()
    except Exception:
        traceback.print_exc()

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    return stdout.getvalue() + stderr.getvalue()
