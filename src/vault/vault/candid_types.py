from kybra import (
    Async,
    Opt,
    Principal,
    Record,
    Service,
    Variant,
    Vec,
    blob,
    nat,
    nat64,
    null,
    service_query,
    service_update,
)


class Account(Record):
    owner: Principal
    subaccount: Opt[Vec[nat]]


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


# Define the request and response types for get_transactions


class Spender(Record):
    owner: Principal
    subaccount: Opt[Vec[nat]]


class Burn(Record):
    from_: Account
    memo: Opt[Vec[nat]]
    created_at_time: Opt[nat64]
    amount: nat
    spender: Opt[Spender]


class Mint(Record):
    to: Account
    memo: Opt[Vec[nat]]
    created_at_time: Opt[nat64]
    amount: nat


class Approve(Record):
    fee: Opt[nat]
    from_: Account
    memo: Opt[Vec[nat]]
    created_at_time: Opt[nat64]
    amount: nat
    expected_allowance: Opt[nat]
    expires_at: Opt[nat64]
    spender: Spender


class Transfer(Record):
    to: Account
    fee: Opt[nat]
    from_: Account
    memo: Opt[Vec[nat]]
    created_at_time: Opt[nat64]
    amount: nat
    spender: Opt[Spender]


class Transaction(Record):
    burn: Opt[Burn]
    kind: str
    mint: Opt[Mint]
    approve: Opt[Approve]
    timestamp: nat64
    transfer: Opt[Transfer]


class GetTransactionsResponse(Record):
    first_index: nat
    log_length: nat
    transactions: Vec[Opt[Transaction]]
    archived_transactions: Vec[Opt[Transaction]]


class GetTransactionsRequest(Record):
    start: nat
    length: nat


class ICRCLedger(Service):
    @service_query
    def icrc1_balance_of(self, account: Account) -> nat: ...

    @service_query
    def icrc1_fee(self) -> nat: ...

    @service_update
    def icrc1_transfer(self, args: TransferArg) -> TransferResult: ...

    @service_query
    def get_transactions(
        self, request: GetTransactionsRequest
    ) -> Async[GetTransactionsResponse]: ...


class GetTransactionsResult(Variant, total=False):
    Ok: GetTransactionsResponse
    Err: str
