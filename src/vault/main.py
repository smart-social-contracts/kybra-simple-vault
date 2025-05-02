import traceback 
from pprint import pformat

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
from vault.candid_types import TransferArg, TransferResult, ICRCLedger, Account

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

    Canisters["ckBTC ledger"] or Canisters(_id="ckBTC ledger", principal=CANISTER_PRINCIPALS['ckBTC']['ledger'])
    Canisters["ckBTC indexer"] or Canisters(_id="ckBTC indexer", principal=CANISTER_PRINCIPALS['ckBTC']['indexer'])
    if not app_data().admin_principal:
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
def transfer(to: Principal, amount: nat) -> Async[nat]:

    principal = Canisters["ckBTC ledger"].principal
    ledger = ICRCLedger(Principal.from_str(principal))

    logger.debug(f"Ledger: {ledger}")

    args: TransferArg = TransferArg(
        to=Account(owner=to, subaccount=None),
        amount=amount,
        fee=None,  # Optional fee, will use default
        memo=None,  # Optional memo field
        from_subaccount=None,  # No subaccount specified
        created_at_time=None,  # System will use current time
    )

    logger.debug(f"(1) Transferring {amount} tokens to {to.to_str()}")
    result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)
    logger.debug(f"(2) Transferring {amount} tokens to {to.to_str()}")

    logger.debug(f"result = {result}")
    logger.debug(f"result type = {type(result)}")
    
    # Try to access result members carefully for debugging
    try:
        logger.debug(f"result.Ok = {result.Ok}")
    except Exception as e:
        logger.error(f"Error accessing result.Ok: {e}")
        
    try:
        logger.debug(f"result.Err = {result.Err}")
    except Exception as e:
        logger.error(f"Error accessing result.Err: {e}")

    # Return -1 if there's any exception in processing the result
    try:
        return match(
            result,
            {
                "Ok": lambda result_variant: match(
                    result_variant,
                    {
                        "Ok": lambda tx_id: tx_id,  # Return the transaction ID directly
                        "Err": lambda err: (logger.error(f"Transfer error: {err}"), -1)[1],  # Return -1 on transfer error with logging
                    },
                ),
                "Err": lambda err: (logger.error(f"Call error: {err}"), -1)[1],  # Return -1 on call error with logging
            },
        )
    except Exception as e:
        logger.error(f"Exception in match processing: {e}")
        return -1


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
    logger.info(f"Updating transaction history for {principal_id}...")

    # Get the configured indexer canister ID
    indexer_canister_id = Canisters["ckBTC indexer"].principal
    max_results = 20

    # Query the indexer for transactions
    response = yield get_account_transactions(
        canister_id=indexer_canister_id,
        owner_principal=principal_id,
        max_results=max_results
    )

    logger.debug(f"Response: {response}")

    # Check if we have transactions in the response
    has_transactions = 'transactions' in response and response['transactions']

    if not response or not has_transactions:
        return f"No transactions found for principal {principal_id}"

    # Track new and updated transactions
    new_count = 0
    updated_count = 0

    # Process each transaction and update the database
    transactions = sorted(response['transactions'], key=lambda x: x['id'])
    for tx in transactions:
        try:
            logger.debug(f"Processing transaction {tx['id']}: {pformat(tx)}")
            
            # Extract transaction data using dictionary access
            tx_id = str(tx['id'])
            transaction = tx['transaction']
            timestamp = int(transaction['timestamp']) if 'timestamp' in transaction else 0
            kind = transaction['kind'] if 'kind' in transaction else "unknown"
            
            # Initialize default values
            principal_from = "unknown"
            principal_to = "unknown"
            amount = 0
            
            # Handle different transaction types
            if kind == 'mint':
                # For mint transactions, the recipient is this principal
                principal_to = principal_id
                principal_from = "mint"
                # Use balance as the amount for mint transaction
                amount = response.get('balance', 0)
                logger.debug(f"Processing mint transaction {tx_id} to {principal_to} with amount {amount}")
                
            elif kind == 'burn':
                # For burn transactions, the sender is this principal
                principal_from = principal_id
                principal_to = "burn"
                # Extract amount from burn transaction if available
                if 'burn' in transaction and transaction['burn']:
                    amount = int(transaction['burn'].get('amount', 0))
                logger.debug(f"Processing burn transaction {tx_id} from {principal_from} with amount {amount}")
                
            elif 'transfer' in transaction and transaction['transfer']:
                # Handle transfer transactions
                transfer = transaction['transfer']
                
                # Get principals for from and to accounts
                principal_from = str(transfer['from_']['owner']) if 'from_' in transfer and 'owner' in transfer['from_'] else "unknown"
                principal_to = str(transfer['to']['owner']) if 'to' in transfer and 'owner' in transfer['to'] else "unknown"
                
                # Get amount
                amount = int(transfer['amount']) if 'amount' in transfer else 0
                
                logger.debug(f"Processing transfer transaction {tx_id} from {principal_from} to {principal_to} with amount {amount}")
            else:
                # Skip unknown transaction types
                logger.debug(f"Skipping unknown transaction type: {kind} for tx {tx_id}")
                continue

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
                
                # Update balances based on transaction type
                some_balance_update = False
                if kind == 'mint':
                    # For mint, only update the recipient's balance
                    balance_to = Balance[principal_to] or Balance(_id=principal_to, amount=0)
                    balance_to.amount = balance_to.amount + amount
                    some_balance_update = True
                    logger.debug(f"Updated balance for {principal_to} to {balance_to.amount}")
                elif kind == 'burn':
                    # For burn, only update the sender's balance
                    balance_from = Balance[principal_from] or Balance(_id=principal_from, amount=0)
                    balance_from.amount = balance_from.amount - amount
                    some_balance_update = True
                    logger.debug(f"Updated balance for {principal_from} to {balance_from.amount}")
                elif kind == 'transfer':
                    '''
                    user deposits in the vault => balance of user increases
                    vault transfers to user => balance of user decreases
                    '''
                    
                    if principal_id == principal_to:
                        balance_from = Balance[principal_from] or Balance(_id=principal_from, amount=0)
                        balance_from.amount = balance_from.amount + amount
                        some_balance_update = True
                        logger.debug(f"Updated balance for {principal_from} to {balance_from.amount}")

                    if principal_id == principal_from:
                        balance_to = Balance[principal_to] or Balance(_id=principal_to, amount=0)
                        balance_to.amount = balance_to.amount - amount
                        some_balance_update = True
                        logger.debug(f"Updated balance for {principal_to} to {balance_to.amount}")

                logger.info(f'Processed transaction {tx_id}: kind={kind}, amount={amount}, from={principal_from}, to={principal_to}')
                if not some_balance_update:
                    logger.warning(f"No balance updates for transaction {tx_id}")

        
        except Exception as e:
            logger.error(f"Error processing transaction {tx_id}: {e}\n {traceback.format_exc()}")

    result = f"Processed {len(transactions)} transactions: {new_count} new, {updated_count} updated"
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
