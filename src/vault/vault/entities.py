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

    scan_end_tx_id = Integer()
    scan_start_tx_id = Integer()
    scan_oldest_tx_id = Integer()


"""


recent_history_end_tx_id
recent_history_start_tx_id => needs to catch up to history_end_tx_id
...

old_history_end_tx_id
old_history_start_tx_id => needs to catch up to oldest_tx_id


Algorithm:
query with start_tx_id = None
the query returns transacions, get the batch_oldest_tx_id

if batch_oldest_tx_id == oldest_tx_id:
    exit

"""


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


"""
Stores the number of tokens deposited into the vault for each user.
Vault balance is updated when:
- user deposits in the vault
- vault transfers to user

However, note that Balance["vault"] is the total number of token deposit in the vault.
"""


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
