from kybra_simple_db import (
    Boolean,
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


class TestModeData(Entity, TimestampedMixin):
    """Stores test mode configuration and state."""

    test_mode_enabled = Boolean(default=False)
    tx_id = Integer(default=0)


class Canisters(Entity, TimestampedMixin):
    """Represents external canisters (e.g., ckBTC ledger, indexer) linked to the vault."""

    principal = String()


def app_data():
    """Retrieves the singleton ApplicationData instance, creating it if it doesn't exist."""
    return ApplicationData["main"] or ApplicationData(_id="main")


def test_mode_data():
    """Retrieves the singleton TestModeData instance, creating it if it doesn't exist."""
    return TestModeData["main"] or TestModeData(_id="main")


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


def test_mode_stats():
    """Gathers and returns various statistics from the vault's entities."""
    return {
        "test_mode_data": test_mode_data().to_dict(),
    }
