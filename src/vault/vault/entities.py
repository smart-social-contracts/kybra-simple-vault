from kybra_simple_db import (
    Entity,
    Integer,
    ManyToMany,
    OneToMany,
    String,
    TimestampedMixin,
)


class ApplicationData(Entity, TimestampedMixin):
    admin_principal = String()
    max_results = Integer()
    max_iteration_count = Integer()

    scan_end_tx_id = Integer(default=0)
    scan_start_tx_id = Integer(default=0)
    scan_oldest_tx_id = Integer(default=0)


class Canisters(Entity, TimestampedMixin):
    principal = String()


def app_data():
    return ApplicationData["main"] or ApplicationData(_id="main")


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
    canister = OneToMany("Canister", "balances")


def stats():
    return {
        "app_data": app_data().to_dict(),
        "balances": [_.to_dict() for _ in Balance.instances()],
        "vault_transactions": [_.to_dict() for _ in VaultTransaction.instances()],
        "canisters": [_.to_dict() for _ in Canisters.instances()],
    }
