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
    text,
)

# Define Candid record types for stats


class CanisterRecord(Record):
    id: text
    principal: Principal


class BalanceRecord(Record):
    principal_id: Principal
    amount: int


class TransactionRecord(Record):
    id: nat
    amount: int
    timestamp: nat


class AppDataRecord(Record):
    admin_principal: Principal
    max_results: nat
    max_iteration_count: nat
    scan_end_tx_id: nat
    scan_start_tx_id: nat
    scan_oldest_tx_id: nat


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
    canisters: Vec[CanisterRecord]


class TransactionIdRecord(Record):
    transaction_id: nat


class TransactionSummaryRecord(Record):
    new_txs_count: nat


class TransactionsListRecord(Record):
    transactions: Vec[TransactionRecord]


# Generic response type for API responses
class ResponseData(Variant, total=False):
    TransactionId: TransactionIdRecord
    TransactionSummary: TransactionSummaryRecord
    Balance: BalanceRecord
    Transactions: Vec[TransactionRecord]
    Stats: StatsRecord
    Error: str
    Message: str


class Response(Record):
    success: bool
    data: ResponseData


# ICRC standard types


class ICRCLedger(Service):
    @service_query
    def icrc1_balance_of(self, account: Account) -> nat: ...

    @service_query
    def icrc1_fee(self) -> nat: ...

    @service_update
    def icrc1_transfer(self, args: TransferArg) -> TransferResult: ...


class Transaction(Record):
    burn: Opt[Burn]
    kind: str
    mint: Opt[Mint]
    approve: Opt[Approve]
    timestamp: nat64
    transfer: Opt[Transfer]


class AccountTransaction(Record):
    id: nat
    transaction: Transaction


class GetAccountTransactionsRequest(Record):
    account: Account
    start: Opt[nat]
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
    ) -> Async[GetTransactionsResult]: ...
