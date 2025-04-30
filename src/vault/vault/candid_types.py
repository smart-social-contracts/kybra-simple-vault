from kybra import (
    Record,
    nat,
    text,
    Opt,
    Vec,
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


class StatsRecord(Record):
    app_data: AppDataRecord
    balances: Vec[BalanceRecord]
    vault_transactions: Vec[TransactionRecord]
    canisters: Vec[CanisterRecord]