from kybra import (
    Async,
    Principal,
    Record,
    Service,
    Variant,
    Vec,
    nat,
    nat64,
    service_query,
    service_update,
    text,
)


class TransactionRecord(Record):
    id: nat
    amount: int
    timestamp: nat64


class BalanceRecord(Record):
    principal_id: Principal
    amount: int


class CanisterRecord(Record):
    id: text
    principal: Principal


class AppDataRecord(Record):
    admin_principals: Vec[Principal]
    max_results: nat
    max_iteration_count: nat
    scan_end_tx_id: nat
    scan_start_tx_id: nat
    scan_oldest_tx_id: nat
    sync_status: text
    sync_tx_id: nat


class StatsRecord(Record):
    app_data: AppDataRecord
    balances: Vec[BalanceRecord]
    canisters: Vec[CanisterRecord]


class TransactionIdRecord(Record):
    transaction_id: nat


class TransactionSummaryRecord(Record):
    new_txs_count: nat
    sync_status: text
    scan_end_tx_id: nat


class ResponseData(Variant, total=False):
    TransactionId: TransactionIdRecord
    TransactionSummary: TransactionSummaryRecord
    Balance: BalanceRecord
    Transactions: Vec[TransactionRecord]
    Stats: StatsRecord
    Error: text
    Message: text


class Response(Record):
    success: bool
    data: ResponseData


# Define the vault service interface
class Vault(Service):
    @service_query
    def status(self) -> Response: ...

    @service_query
    def get_balance(self, principal: Principal) -> Response: ...

    @service_query
    def get_transactions(self, principal: Principal) -> Response: ...

    @service_update
    def transfer(self, principal: Principal, amount: nat) -> Async[Response]: ...
