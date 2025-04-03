from vault.constants import CKBTC_CANISTER
import utils_icp
from kybra_simple_db import *  # TODO
import vault.services as services
from vault.entities import app_data, Transaction, Balance
from kybra import (
    Async,
    CallResult,
    match,
    Opt,
    Principal,
    Record,
    Service,
    service_query,
    service_update,
    Variant,
    nat,
    nat64,
    update,
    query,
    blob,
    null,
    ic,
    heartbeat,
    void,
    StableBTreeMap
)

from kybra_simple_logging import get_logger, set_log_level

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


class Account(Record):
    owner: Principal
    subaccount: Opt[blob]


class TransferArg(Record):
    to: Account
    fee: Opt[nat]
    memo: Opt[nat64]
    from_subaccount: Opt[blob]
    created_at_time: Opt[nat64]
    amount: nat


class BadFeeRecord(Record):
    expected_fee: nat


class BadBurnRecord(Record):
    min_burn_amount: nat


class InsufficientFundsRecord(Record):
    balance: nat


class DuplicateRecord(Record):
    duplicate_of: nat


class GenericErrorRecord(Record):
    error_code: nat
    message: str


class TransferError(Variant, total=False):
    BadFee: BadFeeRecord
    BadBurn: BadBurnRecord
    InsufficientFunds: InsufficientFundsRecord
    TooOld: null
    CreatedInFuture: null
    Duplicate: DuplicateRecord
    TemporarilyUnavailable: null
    GenericError: GenericErrorRecord


class TransferResult(Variant, total=False):
    Ok: nat
    Err: TransferError


class ICRCLedger(Service):
    @service_query
    def icrc1_balance_of(self, account: Account) -> nat:
        ...

    @service_query
    def icrc1_fee(self) -> nat:
        ...

    @service_update
    def icrc1_transfer(self, args: TransferArg) -> TransferResult:
        ...


@query
def get_canister_id() -> Async[Principal]:
    return ic.id()


def _stats():
    return {
        'app_data': app_data().to_dict(),
        'balances': [_.to_dict() for _ in Balance.instances()],
        'transactions': [_.to_dict() for _ in Transaction.instances()]
    }


@query
def get_canister_balance() -> Async[str]:
    # TODO: this one doesn't work but it doesn't matter... try with call_raw
    ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))
    account = Account(owner=ic.id(), subaccount=None)

    result: CallResult[nat] = yield ledger.icrc1_balance_of(account)

    return match(result, {
        "Ok": lambda ok: str(ok),
        "Err": lambda err: "-1"  # Return -1 balance on error
    })


@update
def do_transfer(to: Principal, amount: nat) -> Async[nat]:
    ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))

    args: TransferArg = TransferArg(
        to=Account(owner=to, subaccount=None),
        amount=amount,
        fee=None,  # Optional fee, will use default
        memo=None,  # Optional memo field
        from_subaccount=None,  # No subaccount specified
        created_at_time=None  # System will use current time
    )

    result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

    return match(result, {
        "Ok": lambda ok: 0,
        "Err": lambda err: -1
    })


@update
def get_transactions(start: nat, length: nat) -> Async[str]:
    ret = yield utils_icp.get_transactions(start, length)
    return str(ret)


# @heartbeat # TODO: Disable hearbeat for now
# def heartbeat_() -> Async[void]:
#     yield services.transactions_tracker_hearbeat()


@update
def check_transactions() -> Async[str]:
    ret = yield services.TransactionTracker().check_transactions()
    return str(ret)


@query
def stats() -> str:
    return str(_stats())

def _is_admin(principal: str) -> bool:
    return app_data().admin_principal == principal

@update
def set_admin(principal: Principal) -> str:
    principal_str = principal.to_str()
    if not app_data().admin_principal or _is_admin():
        logger.info(f"Setting admin from {app_data().admin_principal} to {principal.to_str()}")
        app_data().admin_principal = principal.to_str()
        return str(_stats())
    raise ValueError(f"Caller {ic.id().to_str()} is not the current admin principal {app_data().admin_principal}")


@update
def reset() -> str:
    if not _is_admin():
        raise ValueError(f"Caller {ic.id().to_str()} is not the current admin principal {app_data().admin_principal}")
    services.reset()
    return stats()


@query
def version() -> str:
    return '0.6.62'

# TODO: remove in production
@update
def execute_code(code: str) -> str:
    """Executes Python code and returns the output.

    This is the core function needed for the Kybra Simple Shell to work.
    It captures stdout, stderr, and return values from the executed code.
    """
    import sys
    import io
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
