from kybra import (
    CallResult,
    Principal,
    nat,
    blob,
    ic
)

from vault.constants import CKBTC_CANISTER
from vault.utils import parse_candid


def get_transactions(start: nat, length: nat) -> str:
    # Example: '(record { start = 2_324_900 : nat; length = 2 : nat })'
    candid_args = '(record { start = %s : nat; length = %s : nat })' % (start, length)

    call_result: CallResult[blob] = yield ic.call_raw(
        Principal.from_str(CKBTC_CANISTER),
        "get_transactions",
        ic.candid_encode(candid_args),
        0
    )

    return parse_candid(ic.candid_decode(call_result.Ok))
