import os
import sys
from tests.test_utils import check, test

canister_id = os.environ.get("CANISTER_ID")
this_folder = os.path.dirname(os.path.abspath(__file__))
test_py = open(os.path.join(this_folder, "extension_stress.py")).read()


test(
    "Stress test - extension commit",
    ["dfx", "canister", "call", "canister_main", "extension_commit", test_py],
    "()",
)

test(
    "Stress test - extension run",
    ["dfx", "canister", "call", "canister_main", "extension_run"],
    "",
)
