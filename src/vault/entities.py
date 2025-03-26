from kybra_simple_db import *


class ApplicationData(Entity, TimestampedMixin):
    log_length = Integer(min_value=0)
    admin_principal = String(min_length=2, max_length=50)
    vault_principal = String(min_length=2, max_length=50)
    balance = Integer(min_value=0)
    total_inflow = Integer(min_value=0)
    total_outflow = Integer(min_value=0)


app_data = ApplicationData(_id='main')


# def app_data():
#     global _app_data
#     if not _app_data:
#         _app_data = ApplicationData['main']
#     return _app_data


class Category(Entity, TimestampedMixin):
    name = String(min_length=2, max_length=50)


class Transaction(Entity, TimestampedMixin):
    principal_from = String(min_length=2, max_length=50)
    principal_to = String(min_length=2, max_length=50)
    amount = Integer(min_value=0)
    timestamp = Integer(min_value=0)
    categories = ManyToMany("Category", "transactions")
