import base64

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
    ic
)

from kybra import Principal, query, update, blob, Vec, nat, Record, ic


MAINNET_CKBTC_LEDGER_CANISTER = 'mxzaz-hqaaa-aaaar-qaada-cai'

CKBTC_CANISTER = MAINNET_CKBTC_LEDGER_CANISTER
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


def parse(input_str: str):
    # Field mapping
    field_map = {
        "1_779_015_299": "first_index",
        "2_799_807_105": "log_length",
        "3_331_539_157": "transactions",
        "3_650_848_786": "archived_transactions",
        "2_131_139_013": "callback",
        "2_215_343_202": "start",
        "2_668_074_214": "length"
    }

    # Clean up lines
    lines = [line.strip().strip(';') for line in input_str.splitlines() if '=' in line]

    # Output dictionary
    output = {
        "transactions": [],
        "archived_transactions": []
    }

    # Temporary storage for archived_transaction
    archived = {}

    for line in lines:
        parts = line.split('=', 1)
        key = parts[0].strip()
        value = parts[1].strip()

        if key == "1_779_015_299":
            output["first_index"] = value.split(':')[0].strip()
        elif key == "2_799_807_105":
            output["log_length"] = value.split(':')[0].strip()
        elif key == "3_650_848_786":
            pass  # Skip vector keyword line
        elif key == "2_131_139_013":
            value = value.replace('func', '').strip()
            principal, method = value.split('"')[1], value.split('.')[-1]
            archived["callback"] = {
                "principal": principal,
                "code": method
            }
        elif key == "2_215_343_202":
            archived["start"] = value.split(':')[0].strip()
        elif key == "2_668_074_214":
            archived["length"] = value.split(':')[0].strip()

    # Only add archived transaction if callback was found
    if "callback" in archived:
        output["archived_transactions"].append(archived)

    return output


@update
def my_get_transactions(
    start: nat, length: nat
) -> str:
    # Example: '(record { start = 2_324_900 : nat; length = 2 : nat })'
    candid_args = '(record { start = %s : nat; length = %s : nat })' % (start, length)

    call_result: CallResult[blob] = yield ic.call_raw(
        Principal.from_str(CKBTC_CANISTER),
        "get_transactions",
        ic.candid_encode(candid_args),
        0
    )

    # response = parse(ic.candid_decode(call_result.Ok))
    return str(ic.candid_decode(call_result.Ok))

    # return match(
    #     call_result,
    #     {
    #         "Ok": lambda ok: str(ic.candid_decode(ok)),
    #         "Err": lambda err: str(err),
    #     },
    # )

    # if call_result.Err:
    #     return str(call_result.Err)

    # # response: str = parse_response(ic.candid_decode(call_result.Ok))
    # response: str = "test"

    # return str(response)

    # match(
    #     call_result,
    #     {
    #         "Ok": lambda ok: {
    #             "Ok": response
    #         },
    #         "Err": lambda err: {"Err": err},
    #     },
    # )


@query
def version() -> str:
    return '0.6.46'
