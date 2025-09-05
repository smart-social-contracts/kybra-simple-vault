"""
This is an example of how to interact with the vault canister from an external canister.
"""

from kybra import (
    Async,
    CallResult,
    Principal,
    Record,
    ic,
    update,
)
from vault_candid_types import (
    Response,
    Vault,
)


# Define test results container
class VaultTestResults(Record):
    status_response: Response
    balance_response: Response
    transactions_response: Response


@update
def run_vault_tests(vault_canister_id: Principal) -> Async[VaultTestResults]:
    """Test interacting with the vault canister

    Args:
        vault_canister_id: Principal ID of the vault canister to test

    Returns:
        VaultTestResults with the response from calling status() on the vault
    """

    # Get a reference to the vault canister
    vault = Vault(vault_canister_id)

    # Test 1: Get vault status
    status_result: CallResult[Response] = yield vault.status()

    # Test 2: Get vault balance
    balance_result: CallResult[Response] = yield vault.get_balance(ic.caller())

    # Test 3: Get vault transactions
    transactions_result: CallResult[Response] = yield vault.get_transactions(
        ic.caller()
    )

    # Check the status result
    if status_result.Ok is not None:
        # We got a successful response
        status_response = status_result.Ok
        ic.print(f"Status Ok response: {status_response}")

        # Parse the data of StatsRecord object
        if "Stats" in status_response["data"]:
            stats = status_response["data"]["Stats"]
            ic.print("\n=== Stats Record Details ===")

            # AppData details
            app_data = stats["app_data"]
            ic.print(f"Admin Principals: {app_data['admin_principals']}")
            ic.print(f"Max Results: {app_data['max_results']}")
            ic.print(f"Sync Status: {app_data['sync_status']}")
            ic.print(f"Sync Transaction ID: {app_data['sync_tx_id']}")

            # Balances information
            ic.print(f"\nBalances Count: {len(stats['balances'])}")
            for idx, balance in enumerate(stats["balances"]):
                ic.print(
                    f"  Balance {idx+1}: Principal: {balance['principal_id']}, Amount: {balance['amount']}"
                )

            # Canisters information
            ic.print(f"\nCanisters Count: {len(stats['canisters'])}")
            for idx, canister in enumerate(stats["canisters"]):
                ic.print(
                    f"  Canister {idx+1}: ID: {canister['id']}, Principal: {canister['principal']}"
                )
        else:
            ic.print("No Stats data found in the response")

    if balance_result.Ok is not None:
        # We got a successful response
        balance_response = balance_result.Ok
        ic.print(f"Balance Ok response: {balance_response}")

    if transactions_result.Ok is not None:
        # We got a successful response
        transactions_response = transactions_result.Ok
        ic.print(f"Transactions Ok response: {transactions_response}")

    if (
        transactions_result.Err is not None
        or balance_result.Err is not None
        or status_result.Err is not None
    ):
        raise Exception("Error from vault")

    # Return original response objects from the vault
    return VaultTestResults(
        status_response=status_response,
        balance_response=balance_response,
        transactions_response=transactions_response,
    )
