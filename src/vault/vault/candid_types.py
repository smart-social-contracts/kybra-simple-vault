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

# Basic Data Records


# Record representing a canister (ledger or indexer) on the Internet Computer.
class CanisterRecord(Record):
    id: text
    principal: Principal


# Record containing balance information for a principal (user).
class BalanceRecord(Record):
    principal_id: Principal
    amount: int


# Record of a simple transaction with basic details.
class TransactionRecord(Record):
    id: nat
    amount: int
    timestamp: nat


# Application metadata containing settings and status information.
class AppDataRecord(Record):
    admin_principal: Principal
    max_results: nat
    max_iteration_count: nat
    scan_end_tx_id: nat
    scan_start_tx_id: nat
    scan_oldest_tx_id: nat
    sync_status: text
    sync_tx_id: nat


# Statistics and state information for the application.
class StatsRecord(Record):
    app_data: AppDataRecord
    balances: Vec[BalanceRecord]
    canisters: Vec[CanisterRecord]


# Simple record containing a transaction ID.
class TransactionIdRecord(Record):
    transaction_id: nat


# Summary information about transactions.
class TransactionSummaryRecord(Record):
    new_txs_count: nat
    sync_status: text
    scan_end_tx_id: nat


# Container for a list of transaction records.
class TransactionsListRecord(Record):
    transactions: Vec[TransactionRecord]


# ICRC Token Standard


# ICRC-1 standard account representation with owner principal and optional subaccount.
class Account(Record):
    owner: Principal
    subaccount: Opt[Vec[nat]]


# Represents a spender for ICRC-2 approvals.
class Spender(Record):
    owner: Principal
    subaccount: Opt[Vec[nat]]


# Arguments for ICRC-1 transfer operations.
class TransferArg(Record):
    to: Account
    fee: Opt[nat]
    memo: Opt[nat64]
    from_subaccount: Opt[blob]
    created_at_time: Opt[nat64]
    amount: nat


# Transaction Types


# Represents a token transfer between accounts.
class Transfer(Record):
    to: Account
    fee: Opt[nat]
    from_: Account
    memo: Opt[Vec[nat]]
    created_at_time: Opt[nat64]
    amount: nat
    spender: Opt[Spender]


# Represents a token minting operation.
class Mint(Record):
    to: Account
    memo: Opt[Vec[nat]]
    created_at_time: Opt[nat64]
    amount: nat


# Represents a token burning operation.
class Burn(Record):
    from_: Account
    memo: Opt[Vec[nat]]
    created_at_time: Opt[nat64]
    amount: nat
    spender: Opt[Spender]


# Represents an ICRC-2 approval operation.
class Approve(Record):
    fee: Opt[nat]
    from_: Account
    memo: Opt[Vec[nat]]
    created_at_time: Opt[nat64]
    amount: nat
    expected_allowance: Opt[nat]
    expires_at: Opt[nat64]
    spender: Spender


# Comprehensive transaction record containing all possible transaction types.
class Transaction(Record):
    burn: Opt[Burn]
    kind: str
    mint: Opt[Mint]
    approve: Opt[Approve]
    timestamp: nat64
    transfer: Opt[Transfer]


# Transaction associated with a specific account.
class AccountTransaction(Record):
    id: nat
    transaction: Transaction


# Error Records


# Error when incorrect fee is provided.
class BadFeeRecord(Record):
    expected_fee: nat


# Error when burn amount is below minimum threshold.
class BadBurnRecord(Record):
    min_burn_amount: nat


# Error when account has insufficient funds for the operation.
class InsufficientFundsRecord(Record):
    balance: nat


# Error indicating a duplicate transaction.
class DuplicateRecord(Record):
    duplicate_of: nat


# General purpose error with a code and message.
class GenericErrorRecord(Record):
    error_code: nat
    message: str


# ICRC-1 standard transfer error variants.
class TransferError(Variant, total=False):
    BadFee: BadFeeRecord
    BadBurn: BadBurnRecord
    InsufficientFunds: InsufficientFundsRecord
    TooOld: null
    CreatedInFuture: null
    Duplicate: DuplicateRecord
    TemporarilyUnavailable: null
    GenericError: GenericErrorRecord


# ICRC-1 transfer result - either a success with transaction ID or an error.
class TransferResult(Variant, total=False):
    Ok: nat
    Err: TransferError


# Response Types


# Container for various response data types that can be returned by the API.
class ResponseData(Variant, total=False):
    TransactionId: TransactionIdRecord
    TransactionSummary: TransactionSummaryRecord
    Balance: BalanceRecord
    Transactions: Vec[TransactionRecord]
    Stats: StatsRecord
    Error: str
    Message: str


# Standard API response with success flag and data payload.
class Response(Record):
    success: bool
    data: ResponseData


# Transaction History


# Request parameters for retrieving account transaction history.
class GetAccountTransactionsRequest(Record):
    account: Account
    start: Opt[nat]
    max_results: nat


# Response containing transaction history for an account.
class GetAccountTransactionsResponse(Record):
    balance: nat
    transactions: Vec[AccountTransaction]
    oldest_tx_id: Opt[nat]


# Result of a get_transactions request - either success with data or an error message.
class GetTransactionsResult(Variant):
    Ok: GetAccountTransactionsResponse
    Err: str


# Service Definitions


# Interface for the ICRC-1 token ledger canister.
class ICRCLedger(Service):
    @service_query
    def icrc1_balance_of(self, account: Account) -> nat: ...

    @service_query
    def icrc1_fee(self) -> nat: ...

    @service_update
    def icrc1_transfer(self, args: TransferArg) -> TransferResult: ...


# Interface for the ICRC transaction indexer service.
class ICRCIndexer(Service):
    @service_query
    def get_account_transactions(
        self, request: GetAccountTransactionsRequest
    ) -> Async[GetTransactionsResult]: ...
