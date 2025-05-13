import traceback
import json

from kybra import (
    Async,
    nat,
    Principal,
    Record,
    Service,
    Variant,
    Vec,
    nat64,
    update,
    void,
    service_query,
    service_update,
    ic,
    CallResult,
    Opt,
    text
)


# Define the vault service interface based on the vault's candid_types.py

class TransactionRecord(Record):
    id: nat
    amount: int
    timestamp: nat64


class BalanceRecord(Record):
    principal_id: Principal
    amount: int


class CanisterRecord(Record):
    id: text
    principal: Principal


class AppDataRecord(Record):
    admin_principal: Principal
    max_results: nat
    max_iteration_count: nat
    scan_end_tx_id: nat
    scan_start_tx_id: nat
    scan_oldest_tx_id: nat
    sync_status: text
    sync_tx_id: nat


class StatsRecord(Record):
    app_data: AppDataRecord
    balances: Vec[BalanceRecord]
    canisters: Vec[CanisterRecord]


class TransactionIdRecord(Record):
    transaction_id: nat


class TransactionSummaryRecord(Record):
    new_txs_count: nat
    sync_status: text
    scan_end_tx_id: nat


class ResponseData(Variant, total=False):
    TransactionId: TransactionIdRecord
    TransactionSummary: TransactionSummaryRecord
    Balance: BalanceRecord
    Transactions: Vec[TransactionRecord]
    Stats: StatsRecord
    Error: text
    Message: text


class Response(Record):
    success: bool
    data: ResponseData


# Define test results container
class VaultTestResults(Record):
    status_response: Response
    # Additional fields can be added when more tests are implemented
    # balance_response: Response
    # transactions_response: Response


# Define the vault service interface
class VaultService(Service):
    @service_query
    def status(self) -> Response: ...
    
    @service_query
    def get_balance(self, principal: Principal) -> Response: ...
    
    @service_query
    def get_transactions(self, principal: Principal) -> Response: ...
    
    @service_update
    def transfer(self, principal: Principal, amount: nat) -> Async[Response]: ...


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
        else:
            # We got an error message
            error_message = status_result.Err
            ic.print(f"Status Err response: {error_message}")
            
            # Create a proper Response object with the error message
            error_data = ResponseData(Error=f"Error from vault: {error_message}")
            status_response = Response(success=False, data=error_data)
        
        # Return original response objects from the vault
        return VaultTestResults(
            status_response=status_response
        )
        
    except Exception as e:
        ic.print(f"Error: {str(e)}\n{traceback.format_exc()}")
        # Create a failed response with error message
        error_msg = f"Error: {str(e)}"
        error_data = ResponseData(Error=error_msg)
        error_response = Response(success=False, data=error_data)
        
        return VaultTestResults(
            status_response=error_response
        )
