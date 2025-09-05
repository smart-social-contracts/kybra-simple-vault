from kybra_simple_db import (
    Entity,
    Integer,
    ManyToMany,
    OneToMany,
    String,
    TimestampedMixin,
)


class Admin(Entity, TimestampedMixin):
    """Stores admin principal IDs with access to vault administrative functions."""
    
    principal_id = String()


class ApplicationData(Entity, TimestampedMixin):
    """Stores global application configuration and synchronization state."""

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
        "app_data": app_data().to_dict(),
        "balances": [_.to_dict() for _ in Balance.instances()],
        "vault_transactions": [_.to_dict() for _ in VaultTransaction.instances()],
        "canisters": [_.to_dict() for _ in Canisters.instances()],
    }
