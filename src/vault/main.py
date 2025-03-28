from vault.utils import log
from vault.services import TransactionTracker, transactions_tracker_hearbeat
from vault.entities import app_data
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

if not app_data().vault_principal:
    app_data().vault_principal = ic.id().to_str()

# import utils_icp


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


# @query
# def get_canister_balance() -> Async[nat]:
#     # TODO: this one doesn't work but it doesn't matter...
#     ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))
#     account = Account(owner=ic.id(), subaccount=None)

#     result: CallResult[nat] = yield ledger.icrc1_balance_of(account)

#     return match(result, {
#         "Ok": lambda ok: ok,
#         "Err": lambda err: -1  # Return -1 balance on error
#     })


# @update
# def do_transfer(to: Principal, amount: nat) -> Async[nat]:
#     ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))

#     args: TransferArg = TransferArg(
#         to=Account(owner=to, subaccount=None),
#         amount=amount,
#         fee=None,  # Optional fee, will use default
#         memo=None,  # Optional memo field
#         from_subaccount=None,  # No subaccount specified
#         created_at_time=None  # System will use current time
#     )

#     result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

#     return match(result, {
#         "Ok": lambda ok: 0,
#         "Err": lambda err: -1
#     })


# @update
# def get_transactions(start: nat, length: nat) -> str:
#     return str(utils_icp.get_transactions(start, length))


@heartbeat
def heartbeat_() -> Async[void]:
    yield transactions_tracker_hearbeat()


@update
def check_transactions() -> Async[str]:
    ret = yield TransactionTracker().check_transactions()
    return str(ret)


@query
def stats() -> str:
    return str(app_data().to_dict())


@update
def reset() -> str:
    TransactionTracker().reset(ic.id().to_str())
    return stats()


@query
def version() -> str:
    return '0.6.61'
