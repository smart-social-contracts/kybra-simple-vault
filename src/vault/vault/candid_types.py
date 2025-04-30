from kybra import (
    Record,
    nat,
    text,
    Opt,
    Principal,
    blob,
    nat64,
    Vec,
    Variant,
    null,
    Service,
    service_method,
    service_query,
    service_update,
    Async
)

# Define Candid record types for stats


class CanisterRecord(Record):
    _id: text
    principal: text


class BalanceRecord(Record):
    principal_id: text
    amount: nat


class TransactionRecord(Record):
    _id: text
    principal_from: text
    principal_to: text
    amount: nat
    timestamp: nat
    kind: text


class AppDataRecord(Record):
    admin_principal: Opt[text]


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


class StatsRecord(Record):
    app_data: AppDataRecord
    balances: Vec[BalanceRecord]
    vault_transactions: Vec[TransactionRecord]
    canisters: Vec[CanisterRecord]


class ICRCLedger(Service):
    @service_query
    def icrc1_balance_of(self, account: Account) -> nat: ...

    @service_query
    def icrc1_fee(self) -> nat: ...

    @service_update
    def icrc1_transfer(self, args: TransferArg) -> TransferResult: ...


class Transaction(Record):
    burn: Opt[null]
    kind: str
    mint: Opt[null]
    approve: Opt[null]
    timestamp: nat64
    transfer: Opt[Transfer]


class AccountTransaction(Record):
    id: nat
    transaction: Transaction


class GetAccountTransactionsRequest(Record):
    account: Account
    max_results: nat


class GetAccountTransactionsResponse(Record):
    balance: nat
    transactions: Vec[AccountTransaction]
    oldest_tx_id: Opt[nat]


class GetTransactionsResult(Variant):
    Ok: GetAccountTransactionsResponse
    Err: str


class ICRCIndexer(Service):
    @service_query
    def get_account_transactions(
        self, request: GetAccountTransactionsRequest
    ) -> Async[GetTransactionsResult]:
        ...
