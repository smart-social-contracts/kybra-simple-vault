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


# Define your field mappings based on the CKBTC canister's Candid interface
RESPONSE_FIELD_MAPPINGS = {
    1_779_015_299: "oldest_tx_id",
    2_799_807_105: "total_transactions",
    3_650_848_786: "transactions",
}

TRANSACTION_FIELD_MAPPINGS = {
    2_215_343_202: "start",
    2_668_074_214: "length",
    2_131_139_013: "func",
}


class ExecuteCallRawResult(Variant, total=False):
    Ok: str
    Err: str


def map_fields(obj, field_mappings):
    """Maps numeric field IDs to human-readable names."""
    return {
        field_mappings.get(key, key): value
        for key, value in obj.items()
    }


def parse_transactions(transactions):
    """Parses a list of transaction records."""
    return [
        map_fields(tx, TRANSACTION_FIELD_MAPPINGS)
        for tx in transactions
    ]


def parse_response(response):
    """Parses the entire response structure."""
    parsed = map_fields(response, RESPONSE_FIELD_MAPPINGS)

    if "transactions" in parsed:
        parsed["transactions"] = parse_transactions(parsed["transactions"])

    return parsed


@update
def my_get_transactions(
    start: nat, length: nat
) -> Async[ExecuteCallRawResult]:
    # Correct argument encoding using Python dict
    candid_args = {"start": start, "length": length}

    call_result: CallResult[blob] = yield ic.call_raw(
        Principal.from_str(CKBTC_CANISTER),
        "get_transactions",
        ic.candid_encode(candid_args),
        0
    )

    if call_result.Err:
        return {"Err": call_result.Err}

    # response: str = parse_response(ic.candid_decode(call_result.Ok))
    response: str = "test"

    return {"Ok": response}

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
    return '0.6.37'
