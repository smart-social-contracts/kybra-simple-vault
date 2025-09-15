from kybra_simple_db import (
    Entity,
    Integer,
    ManyToMany,
    OneToMany,
    String,
    TimestampedMixin,
)


class ApplicationData(Entity, TimestampedMixin):
    """Stores global application configuration and synchronization state."""

    admin_principal = String()
    max_results = Integer()
    max_iteration_count = Integer()

    scan_end_tx_id = Integer(default=0)
    scan_start_tx_id = Integer(default=0)
    scan_oldest_tx_id = Integer(default=0)


class Canisters(Entity, TimestampedMixin):
    """Represents external canisters (e.g., ckBTC ledger, indexer) linked to the vault."""

    principal = String()


def app_data():
    """Retrieves the singleton ApplicationData instance, creating it if it doesn't exist."""
    return ApplicationData["main"] or ApplicationData(_id="main")


class Category(Entity, TimestampedMixin):
    """Defines a category that can be associated with transactions."""

    name = String()


class VaultTransaction(Entity, TimestampedMixin):
    """Records details of an ICRC-1 transaction relevant to the vault's operations."""

    principal_from = String()
    principal_to = String()
    amount = Integer(min_value=0)
    timestamp = Integer(min_value=0)
    kind = String()
    categories = ManyToMany("Category", "transactions")


class Balance(Entity, TimestampedMixin):
    """Represents a balance amount, potentially associated with a 'Canister' entity."""

    amount = Integer(default=0)
    canister = OneToMany("Canister", "balances")


def stats():
    """Gathers and returns various statistics from the vault's entities."""
    return {
        "app_data": {
            "_id": app_data()._id,
            "admin_principal": app_data().admin_principal,
            "max_results": app_data().max_results,
            "max_iteration_count": app_data().max_iteration_count,
            "scan_end_tx_id": app_data().scan_end_tx_id,
            "scan_start_tx_id": app_data().scan_start_tx_id,
            "scan_oldest_tx_id": app_data().scan_oldest_tx_id,
        },
        "balances": [{"_id": b._id, "amount": b.amount} for b in Balance.instances()],
        "vault_transactions": [{"_id": t._id, "principal_from": t.principal_from, "principal_to": t.principal_to, "amount": t.amount, "timestamp": t.timestamp, "kind": t.kind} for t in VaultTransaction.instances()],
        "canisters": [{"_id": c._id, "principal": c.principal} for c in Canisters.instances()],
    }
