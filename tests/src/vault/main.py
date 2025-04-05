from kybra import StableBTreeMap, ic, query, update
from kybra_simple_db import *  # TODO

# from tests import (
#     # test_parse_candid
#     test_basic
# )

db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100_000, max_value_size=1_000_000
)
db_audit = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100_000, max_value_size=1_000_000
)

Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)


@query
def greet() -> str:
    ic.print("Hello!")
    return "Hello!"


@update
def run_test(module_name: str) -> int:
    ic.print(f"Running test_{module_name}...")
    return globals()[f"test_{module_name}"].run()
