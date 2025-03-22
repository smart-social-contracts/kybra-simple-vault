from kybra import query, update, Principal, nat64, Opt, Variant, Record, Vec, ic, null, void
from ckbtc_ledger import ckBTC_Ledger, TransferRequest, TransferResponse

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
)


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


def get_canister_balance_2() -> Async[int]:
    # def get_canister_balance_2() -> int:
    ic.print('get_canister_balance_2')
    ledger = ICRCLedger(Principal.from_str('bkyz2-fmaaa-aaaaa-qaaaq-cai'))
    account = Account(owner=ic.id(), subaccount=None)

    ic.print(ic.id())

    result: CallResult[int] = yield ledger.icrc1_balance_of(account)

    ic.print(result)

    return match(result, {
        "Ok": lambda ok: ok,
        "Err": lambda err: 0  # Return 0 balance on error
    })


@query
def get_canister_balance() -> Async[nat]:
    return get_canister_balance_2()


def do_transfer_2(to: Principal, amount: nat) -> Async[int]:
    '''
    transfer the tokens from this canister to `to`
    '''

    ic.print('transfer_2')
    ledger = ICRCLedger(Principal.from_str('mxzaz-hqaaa-aaaar-qaada-cai'))

    ic.print('to = %s' % to)
    ic.print('amount = %d' % amount)

    args: TransferArg = TransferArg(
        to=Account(owner=to, subaccount=None),
        amount=amount,
        fee=None,  # Optional fee, will use default
        memo=None,  # Optional memo field
        from_subaccount=None,  # No subaccount specified
        created_at_time=None  # System will use current time
    )

    result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

    ic.print('result')
    ic.print(str(result))

    return match(result, {
        "Ok": lambda ok: 1,
        "Err": lambda err: 0
    })

# {
#             "BadFee": lambda bad_fee: 0,
#             "BadBurn": lambda bad_burn: 0,
#             "InsufficientFunds": lambda insufficient_funds: 0,
#             "TooOld": lambda too_old: 0,
#             "CreatedInFuture": lambda created_in_future: 0,
#             "Duplicate": lambda duplicate: 0,
#             "TemporarilyUnavailable": lambda temporarily_unavailable: 0,
#             "GenericError": lambda generic_error: 0
#         }


@update
def do_transfer(to: Principal, amount: nat) -> Async[nat]:
    ret = do_transfer_2(to, amount)
    ic.print('ret = %s' % ret)
    return ret

# class TransferResult(Variant):
#     Ok: nat64
#     Err: str


@query
def version() -> str:
    return '0.6.11'


# @update
# def transfer(to: Principal, amount: nat64) -> TransferResult:
#     ic.print('transfer')
#     ic.print(to)
#     ic.print(amount)
#     """Transfers ckBTC to another user using the ckBTC Ledger canister"""
#     caller = ic.caller()

#     # Call the ckBTC ledger canister
#     try:
#         ic.print('1')
#         response = ic.call(
#             Principal.from_str("bkyz2-fmaaa-aaaaa-qaaaq-cai"),  # Local ckBTC Ledger Canister ID
#             "icrc1_transfer",
#             {
#                 "to": {"owner": to, "subaccount": Opt.none()},
#                 "amount": amount,
#                 "fee": Opt.none(),
#                 "memo": Opt.none(),
#                 "from_subaccount": Opt.none(),
#                 "created_at_time": Opt.none()
#             }
#         )
#         ic.print('2')
#         ic.print(str(response))
#         if "Ok" in response:
#             print('3a')
#             return TransferResult.Ok(response["Ok"])
#         else:
#             print('3b')
#             return TransferResult.Err("Transfer failed")
#     except Exception as e:
#         print('4')
#         return TransferResult.Err(str(e))

#     print('0000')
