from kybra_simple_db import *

from vault.constants import CKBTC_CANISTER


class ApplicationData(Entity, TimestampedMixin):
    last_processed_index = Integer(min_value=0, default=0)
    log_length = Integer(min_value=0, default=0)
    admin_principal = String()
    vault_principal = String()
    last_heartbeat_time = Integer(min_value=0, default=0)
    heartbeat_interval_seconds = Integer(min_value=0, default=0)


class LedgerCanister(Entity, TimestampedMixin):
    principal = String()


def app_data():
    return ApplicationData["main"] or ApplicationData(_id="main")


def ledger_canister():
    return LedgerCanister["ckBTC"] or LedgerCanister(
        _id="ckBTC", principal=CKBTC_CANISTER
    )


class Category(Entity, TimestampedMixin):
    name = String()


class VaultTransaction(Entity, TimestampedMixin):
    principal_from = String()
    principal_to = String()
    amount = Integer(min_value=0)
    timestamp = Integer(min_value=0)
    kind = String()
    categories = ManyToMany("Category", "transactions")


class Balance(Entity, TimestampedMixin):
    amount = Integer(default=0)
    currency = String()


def stats():
    return {
        "app_data": app_data().to_dict(),
        "balances": [_.to_dict() for _ in Balance.instances()],
        "vault_transactions": [_.to_dict() for _ in VaultTransaction.instances()],
        "ledger_canisters": [_.to_dict() for _ in LedgerCanister.instances()],
    }
