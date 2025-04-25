from kybra import (
    Async,
    CallResult,
    Opt,
    Principal,
    StableBTreeMap,
    heartbeat,
    ic,
    init,
    match,
    nat,
    query,
    update,
    void,
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
from vault.constants import (
    DO_NOT_IMPLEMENT_HEARTBEAT,
    MAINNET_CKBTC_LEDGER_ID,
    MAINNET_CKBTC_LEDGER_PRINCIPAL,
)
from vault.entities import LedgerCanister, app_data, ledger_canister, stats

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


@init
def init_(
    ledger_canister_id: Opt[str] = None,
    ledger_canister_principal: Opt[Principal] = None,
    admin_principal: Opt[Principal] = None,
    heartbeat_interval_seconds: nat = 0,
) -> void:
    """
    Initializes the vault canister.
    Args:
        ledger_canister_id: The canister ID of the ledger as a string (optional, defaults to mainnet)
        ledger_canister_principal: Principal of the ledger canister (optional, defaults to mainnet principal)
        admin_principal: Principal of the admin (optional)
        heartbeat_interval_seconds: Heartbeat interval (nat)
    """

    if (ledger_canister_id is None and ledger_canister_principal is not None) or (
        ledger_canister_id is not None and ledger_canister_principal is None
    ):
        raise ValueError(
            "Both ledger_canister_id and ledger_canister_principal must be provided or both must be None"
        )

    # Use mainnet ledger's principal and ID if not provided
    actual_ledger_principal: Principal = (
        Principal.from_str(MAINNET_CKBTC_LEDGER_PRINCIPAL)
        if ledger_canister_principal is None
        else ledger_canister_principal
    )
    actual_ledger_id: str = (
        MAINNET_CKBTC_LEDGER_ID if ledger_canister_id is None else ledger_canister_id
    )

    # Use caller as admin if not provided
    actual_admin: Principal = (
        ic.caller() if admin_principal is None else admin_principal
    )

    logger.info(
        f"Initializing with:\n"
        f"  ledger_canister_id: {actual_ledger_id}\n"
        f"  ledger_canister_principal: {actual_ledger_principal.to_str()}\n"
        f"  admin_principal: {actual_admin.to_str()}\n"
        f"  heartbeat_interval_seconds: {heartbeat_interval_seconds}"
    )

    # Store the ledger principal in LedgerCanister
    ledger = LedgerCanister[actual_ledger_id] or LedgerCanister(_id=actual_ledger_id, principal=actual_ledger_principal.to_str())

    logger.info('ledger = %s' % ledger)
    logger.info('ledger.to_dict() = %s' % ledger.to_dict())
    
    ledger = LedgerCanister[actual_ledger_id]
    logger.info('ledger           (loaded) = %s' % ledger)
    logger.info('ledger.to_dict() (loaded) = %s' % ledger.to_dict())


    # Make sure these values are also stored in app_data for persistence
    app_data().ledger_canister_id = actual_ledger_id
    app_data().ledger_canister_principal = actual_ledger_principal.to_str()
    app_data().admin_principal = actual_admin.to_str()
    app_data().heartbeat_interval_seconds = heartbeat_interval_seconds


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
    logger.info('MAINNET_CKBTC_LEDGER_ID = %s' % MAINNET_CKBTC_LEDGER_ID)
    ledger = LedgerCanister[MAINNET_CKBTC_LEDGER_ID]
    logger.info('balance: ledger           = %s' % ledger)
    logger.info('balance: ledger.to_dict() = %s' % ledger.to_dict())
    ledger = ICRCLedger(Principal.from_str(ledger.principal))
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
    ledger = ICRCLedger(Principal.from_str(ledger_canister().principal))

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


@update
def check_transactions() -> Async[str]:
    ret = yield services.TransactionTracker().check_transactions()
    return str(ret)


@query
def get_stats() -> str:
    return str(stats())


@update
def set_admin(principal: Principal) -> str:
    return admin.set_admin(ic.caller().to_str(), principal.to_str())


if not DO_NOT_IMPLEMENT_HEARTBEAT:

    @update
    def set_heartbeat_interval_seconds(seconds: nat) -> nat:
        global heartbeat_interval_seconds
        heartbeat_interval_seconds = admin.set_heartbeat_interval_seconds(
            ic.caller().to_str(), seconds
        )
        return heartbeat_interval_seconds


@update
def reset() -> str:
    return admin.reset(ic.caller().to_str())


@update
def set_ledger_canister(canister_id: str, principal: Principal) -> str:
    return admin.set_ledger_canister(
        ic.caller().to_str(), canister_id, principal.to_str()
    )






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
            ic.print(repr(result))
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