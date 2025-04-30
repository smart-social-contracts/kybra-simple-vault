from kybra_simple_logging import get_canister_logs as _get_canister_logs
from kybra import Opt, Record, Vec, nat, query
from kybra import (
    Async,
    CallResult,
    Principal,
    StableBTreeMap,
    ic,
    match,
    nat,
    query,
    update,
    void,
    Record,
    Opt,
    ic,
    nat,
    nat64,
    nat8,
    null,
    Opt,
    Vec,
    Record,
    Variant,
    Service,
    service_query,
    service_update,
    init,
    text,
)
from typing import Optional, List
from kybra_simple_db import *
from kybra_simple_logging import get_logger, set_log_level, Level

# import vault.admin as admin
# import vault.services as services
# import vault.utils_icp as utils_icp
# import vault.utils_neural as utils_neural
from vault.ic_util_calls import get_account_transactions
from vault.entities import VaultTransaction, Canisters, app_data, Balance
from vault.constants import CANISTER_PRINCIPALS

# import vault.candid_types as candid_types
# from vault.constants import CKBTC_CANISTER, DO_NOT_IMPLEMENT_HEARTBEAT
# from vault.entities import app_data, stats
# Import at the top of the file

from vault.candid_types import (
    CanisterRecord,
    BalanceRecord,
    TransactionRecord,
    AppDataRecord,
    StatsRecord,
)

logger = get_logger(__name__)
set_log_level(Level.DEBUG)


db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100_000, max_value_size=1_000_000
)
db_audit = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100_000, max_value_size=1_000_000
)

# Initialize the database
Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)


@init
def init_() -> void:
    logger.info("Initializing vault...")

    Canisters(_id="ckBTC ledger", principal=CANISTER_PRINCIPALS['ckBTC']['ledger'])
    Canisters(_id="ckBTC indexer", principal=CANISTER_PRINCIPALS['ckBTC']['indexer'])
    app_data().admin_principal = ic.caller().to_str()

    logger.info("Vault initialized.")


@update
def set_canister(canister_name: str, principal_id: Principal) -> str:
    """
    Set or update the principal ID for a specific canister in the Canisters entity.

    Args:
        canister_name: The name of the canister to set/update (e.g., "ckBTC ledger", "ckBTC indexer")
        principal_id: The principal ID of the canister

    Returns:
        Status message
    """
    logger.info(f"Setting canister '{canister_name}' to principal: {principal_id.to_str()}")

    # Check if the canister already exists
    existing_canister = Canisters[canister_name]
    if existing_canister:
        # Update the existing canister record
        existing_canister.principal = principal_id.to_str()
        logger.info(f"Updated existing canister '{canister_name}' with new principal.")
    else:
        # Create a new canister record
        Canisters(_id=canister_name, principal=principal_id.to_str())
        logger.info(f"Created new canister '{canister_name}' with principal.")

    return f"Canister '{canister_name}' principal set to: {principal_id.to_str()}"


@update
def do_transfer(to: Principal, amount: nat) -> Async[nat]:
    from vault.entities import LEDGER_SUITE_canister

    principal = LEDGER_SUITE_canister().principal
    ledger = ICRCLedger(Principal.from_str(principal))

    args: TransferArg = TransferArg(
        to=Account(owner=to, subaccount=None),
        amount=amount,
        fee=None,  # Optional fee, will use default
        memo=None,  # Optional memo field
        from_subaccount=None,  # No subaccount specified
        created_at_time=None,  # System will use current time
    )

    logger.debug(f"Transferring {amount} tokens to {to.to_str()}")
    result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

    # Return the transaction id on success or -1 on error
    return match(
        result,
        {
            "Ok": lambda result_variant: match(
                result_variant,
                {
                    "Ok": lambda tx_id: tx_id,  # Return the transaction ID directly
                    "Err": lambda _: -1,  # Return -1 on transfer error
                },
            ),
            "Err": lambda _: -1,  # Return -1 on call error
        },
    )


@update
def update_transaction_history() -> str:
    return _update_transaction_history(ic.id().to_str())


def _update_transaction_history(principal_id: str) -> str:
    """
    Updates the transaction history for a given principal by querying the ICRC indexer
    and storing the transactions in the VaultTransaction database.

    Args:
        principal_id: The principal ID to update transaction history for

    Returns:
        A status message indicating the number of transactions processed
    """
    ic.print(f"Updating transaction history for {principal_id}...")

    # Get the configured indexer canister ID
    indexer_canister_id = Canisters["ckBTC indexer"].principal
    max_results = 20

    # Query the indexer for transactions
    response = yield get_account_transactions(
        canister_id=indexer_canister_id,
        owner_principal=principal_id,
        max_results=max_results
    )

    ic.print(f"Response: {response}")

    # Check if we have transactions in the response
    has_transactions = 'transactions' in response and response['transactions']

    if not response or not has_transactions:
        return f"No transactions found for principal {principal_id}"

    # Track new and updated transactions
    new_count = 0
    updated_count = 0

    # Process each transaction and update the database
    for tx in response['transactions']:
        # Extract transaction data using dictionary access
        tx_id = str(tx['id'])
        transaction = tx['transaction']

        # Skip if the transaction doesn't have a transfer
        if 'transfer' not in transaction or not transaction['transfer']:
            continue

        transfer = transaction['transfer']

        # Get principals for from and to accounts
        principal_from = str(transfer['from_']['owner']) if 'from_' in transfer and 'owner' in transfer['from_'] else "unknown"
        principal_to = str(transfer['to']['owner']) if 'to' in transfer and 'owner' in transfer['to'] else "unknown"

        # Get amount and timestamp
        amount = int(transfer['amount']) if 'amount' in transfer else 0
        timestamp = int(transaction['timestamp']) if 'timestamp' in transaction else 0
        kind = transaction['kind'] if 'kind' in transaction else "unknown"

        logger.debug(f"Processing transaction {tx_id}")

        # Create or update the VaultTransaction
        existing_tx = VaultTransaction[tx_id]
        if existing_tx:
            # Update existing transaction if needed
            if (
                existing_tx.principal_from != principal_from
                or existing_tx.principal_to != principal_to
                or existing_tx.amount != amount
                or existing_tx.timestamp != timestamp
                or existing_tx.kind != kind
            ):
                existing_tx.principal_from = principal_from
                existing_tx.principal_to = principal_to
                existing_tx.amount = amount
                existing_tx.timestamp = timestamp
                existing_tx.kind = kind
                updated_count += 1
        else:
            # Create new transaction
            VaultTransaction(
                _id=tx_id,
                principal_from=principal_from,
                principal_to=principal_to,
                amount=amount,
                timestamp=timestamp,
                kind=kind
            )
            new_count += 1

            balance_from = Balance[principal_from] or Balance(principal_id=principal_from)
            balance_to = Balance[principal_to] or Balance(principal_id=principal_to)
            balance_from.amount = balance_from.amount - amount
            balance_to.amount = balance_to.amount + amount

            logger.debug(f"Updated balances: {balance_from.amount} for {principal_from}, {balance_to.amount} for {principal_to}")

    result = f"Processed {len(response['transactions'])} transactions: {new_count} new, {updated_count} updated"
    ic.print(result)
    return result


@query
def get_stats() -> StatsRecord:
    """
    Get statistics about the vault's state including balances, transactions, and canister references.

    Returns:
        A record containing vault statistics including app_data, balances, transactions,
        and canister references.
    """
    from vault.entities import stats, app_data, Balance, VaultTransaction, Canisters

    logger.debug("Retrieving vault statistics")

    # Get app_data with proper typing
    app_data_obj = app_data()
    app_data_record = {
        "admin_principal": app_data_obj.admin_principal if hasattr(app_data_obj, "admin_principal") else None,
    }

    # Get balances with proper typing
    balances = []
    for balance in Balance.instances():
        balances.append({
            "principal_id": balance.principal_id,
            "amount": balance.amount,
        })

    # Get transactions with proper typing
    transactions = []
    for tx in VaultTransaction.instances():
        transactions.append({
            "_id": tx._id,
            "principal_from": tx.principal_from,
            "principal_to": tx.principal_to,
            "amount": tx.amount,
            "timestamp": tx.timestamp,
            "kind": tx.kind if hasattr(tx, "kind") else "unknown",
        })

    # Get canisters with proper typing
    canisters = []
    for canister in Canisters.instances():
        canisters.append({
            "_id": canister._id,
            "principal": canister.principal,
        })

    # Return properly typed stats record
    return {
        "app_data": app_data_record,
        "balances": balances,
        "vault_transactions": transactions,
        "canisters": canisters,
    }


@query
def get_balance(principal_id: str) -> nat:
    """
    Get the balance for a specific principal.

    Args:
        principal_id: The principal ID to check balance for

    Returns:
        The current balance amount for the specified principal
    """
    logger.debug(f"Getting balance for principal: {principal_id}")

    # Look up the balance in the database
    balance = Balance[principal_id]

    # Return the balance amount or 0 if not found
    if balance:
        return balance.amount

    return 0


@query
def get_transactions(principal_id: str) -> Vec[TransactionRecord]:
    """
    Get all transactions associated with a specific principal.

    Args:
        principal_id: The principal ID to get transactions for

    Returns:
        A list of transactions where the principal is either sender or receiver
    """
    logger.debug(f"Getting transactions for principal: {principal_id}")

    # Collect all transactions where this principal is involved
    transactions = []

    for tx in VaultTransaction.instances():
        # Check if this principal is either the sender or receiver
        if tx.principal_from == principal_id or tx.principal_to == principal_id:
            transactions.append({
                "_id": tx._id,
                "principal_from": tx.principal_from,
                "principal_to": tx.principal_to,
                "amount": tx.amount,
                "timestamp": tx.timestamp,
                "kind": tx.kind if hasattr(tx, "kind") else "unknown",
            })

    return transactions


# ##### Import Kybra and the internal function #####


# Define the PublicLogEntry class directly in the test canister
class PublicLogEntry(Record):
    timestamp: nat
    level: str
    logger_name: str
    message: str
    id: nat


@query
def get_canister_logs(
        from_entry: Opt[nat] = None,
        max_entries: Opt[nat] = None,
        min_level: Opt[str] = None,
        logger_name: Opt[str] = None,
) -> Vec[PublicLogEntry]:
    """
    Re-export the get_canister_logs query function from the library
    This makes it accessible as a query method on the test canister
    """
    logs = _get_canister_logs(
        from_entry=from_entry,
        max_entries=max_entries,
        min_level=min_level,
        logger_name=logger_name
    )

    # Convert the logs to our local PublicLogEntry type
    return [
        PublicLogEntry(
            timestamp=log["timestamp"],
            level=log["level"],
            logger_name=log["logger_name"],
            message=log["message"],
            id=log["id"],
        )
        for log in logs
    ]
