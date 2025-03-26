import ast
import constants

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


from kybra_simple_db import *  # TODO
db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100_000, max_value_size=1_000_000
)
db_audit = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100_000, max_value_size=1_000_000
)

Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)

import utils_icp
from entities import app_data

# Transaction(_id='...', ..)


CKBTC_CANISTER = constants.MAINNET_CKBTC_LEDGER_CANISTER
# CKBTC_INDEX_CANISTER = 'bkyz2-fmaaa-aaaaa-qaaaq-cai'


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


@query
def get_canister_balance() -> Async[nat]:
    # TODO: this one doesn't work but it doesn't matter...
    ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))
    account = Account(owner=ic.id(), subaccount=None)

    result: CallResult[nat] = yield ledger.icrc1_balance_of(account)

    return match(result, {
        "Ok": lambda ok: ok,
        "Err": lambda err: -1  # Return -1 balance on error
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
def get_transactions(start: nat, length: nat) -> str:
    return str(utils_icp.get_transactions(start, length))

last_heartbeat_time = 0
time_period_seconds = 10


@heartbeat
def heartbeat_() -> void:
    # ic.print("this runs ~1 time per second")
    global last_heartbeat_time
    now = ic.time()
    if (now - last_heartbeat_time) / 1e9 > time_period_seconds:
        last_heartbeat_time = now
    # ic.print("last_heartbeat_time: %s" % last_heartbeat_time)


@query
def get_last_heartbeat_time() -> str:
    return str(last_heartbeat_time / 1e9)

@query
def stats() -> str:
    return str(app_data.to_dict())


@query
def version() -> str:
    return '0.6.51'
