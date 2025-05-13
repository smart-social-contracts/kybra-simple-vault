import json
import traceback

from kybra import (
    Async,
    CallResult,
    Principal,
    ic,
    update,
)

from candid_types import (
    Response,
    ResponseData,
    VaultService,
    VaultTestResults,
)


@update
def run_vault_tests(vault_canister_id: Principal) -> Async[VaultTestResults]:
    """Test interacting with the vault canister

    Args:
        vault_canister_id: Principal ID of the vault canister to test

    Returns:
        VaultTestResults with the response from calling status() on the vault
    """
    try:
        # Get a reference to the vault canister
        vault = VaultService(vault_canister_id)

        # Test 1: Get vault status
        status_result: CallResult[Response] = yield vault.status()

        # Check the status result
        if status_result.Ok is not None:
            # We got a successful response
            status_response = status_result.Ok
            ic.print(f"Status Ok response: {status_response}")

            # Parse the data of StatsRecord object
            if 'Stats' in status_response['data']:
                stats = status_response['data']['Stats']
                ic.print("\n=== Stats Record Details ===")

                # AppData details
                app_data = stats['app_data']
                ic.print(f"Admin Principal: {app_data['admin_principal']}")
                ic.print(f"Max Results: {app_data['max_results']}")
                ic.print(f"Sync Status: {app_data['sync_status']}")
                ic.print(f"Sync Transaction ID: {app_data['sync_tx_id']}")

                # Balances information
                ic.print(f"\nBalances Count: {len(stats['balances'])}")
                for idx, balance in enumerate(stats['balances']):
                    ic.print(f"  Balance {idx+1}: Principal: {balance['principal_id']}, Amount: {balance['amount']}")

                # Canisters information
                ic.print(f"\nCanisters Count: {len(stats['canisters'])}")
                for idx, canister in enumerate(stats['canisters']):
                    ic.print(f"  Canister {idx+1}: ID: {canister['id']}, Principal: {canister['principal']}")
            else:
                ic.print("No Stats data found in the response")


        else:
            # We got an error message
            error_message = status_result.Err
            ic.print(f"Status Err response: {error_message}")

            # Create a proper Response object with the error message
            error_data = ResponseData(Error=f"Error from vault: {error_message}")
            status_response = Response(success=False, data=error_data)

        # Return original response objects from the vault
        return VaultTestResults(status_response=status_response)

    except Exception as e:
        ic.print(f"Error: {str(e)}\n{traceback.format_exc()}")
        # Create a failed response with error message
        error_msg = f"Error: {str(e)}"
        error_data = ResponseData(Error=error_msg)
        error_response = Response(success=False, data=error_data)

        return VaultTestResults(status_response=error_response)
