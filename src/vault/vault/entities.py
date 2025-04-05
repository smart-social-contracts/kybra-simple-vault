from kybra_simple_db import *


class ApplicationData(Entity, TimestampedMixin):
    last_processed_index = Integer(min_value=0, default=0)
    log_length = Integer(min_value=0, default=0)
    admin_principal = String()
    vault_principal = String()
    last_heartbeat_time = Integer(min_value=0, default=0)
    heartbeat_interval_seconds = Integer(min_value=0, default=0)


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
    currency = String()
