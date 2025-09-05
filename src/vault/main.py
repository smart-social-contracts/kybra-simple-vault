import traceback
from functools import wraps
from pprint import pformat

from kybra import (
    Async,
    CallResult,
    Opt,
    Principal,
    StableBTreeMap,
    Tuple,
    Vec,
    ic,
    init,
    nat,
    query,
    update,
    void,
)
from kybra_simple_db import Database
from kybra_simple_logging import get_logger

from vault.candid_types import (
    Account,
    AppDataRecord,
    BalanceRecord,
    CanisterRecord,
    ICRCLedger,
    Response,
    ResponseData,
    StatsRecord,
    TransactionIdRecord,
    TransactionRecord,
    TransactionSummaryRecord,
    TransferArg,
    TransferResult,
)
from vault.constants import CANISTER_PRINCIPALS, MAX_ITERATION_COUNT, MAX_RESULTS
from vault.entities import Admin, Balance, Canisters, VaultTransaction, app_data
from vault.ic_util_calls import get_account_transactions

logger = get_logger(__name__)

storage = StableBTreeMap[str, str](memory_id=1, max_key_size=100, max_value_size=1000)
Database.init(db_storage=storage)


@init
def init_(
    canisters: Opt[Vec[Tuple[str, Principal]]] = None,
    admin_principals: Opt[Vec[Principal]] = None,
    max_results: Opt[nat] = None,
    max_iteration_count: Opt[nat] = None,
) -> void:
    logger.info("Initializing vault...")

    if canisters:
        for canister_name, principal_id in canisters:

            if not Canisters[canister_name]:
                logger.info(
                    f"Creating canister record '{canister_name}' with principal: {principal_id.to_str()}"
                )
                Canisters(_id=canister_name, principal=principal_id.to_str())
            else:
                logger.warning(
                    f"Canister record '{canister_name}' already exists with principal: {Canisters[canister_name].principal}"
                )

    if not Canisters["ckBTC ledger"]:
        logger.info(
            f"Creating canister record 'ckBTC ledger' with principal: {CANISTER_PRINCIPALS['ckBTC']['ledger']}"
        )
        Canisters(_id="ckBTC ledger", principal=CANISTER_PRINCIPALS["ckBTC"]["ledger"])
    else:
        logger.info(
            f"Canister record 'ckBTC ledger' already exists with principal: {Canisters['ckBTC ledger'].principal}"
        )

    if not Canisters["ckBTC indexer"]:
        logger.info(
            f"Creating canister record 'ckBTC indexer' with principal: {CANISTER_PRINCIPALS['ckBTC']['indexer']}"
        )
        Canisters(
            _id="ckBTC indexer", principal=CANISTER_PRINCIPALS["ckBTC"]["indexer"]
        )
    else:
        logger.info(
            f"Canister record 'ckBTC indexer' already exists with principal: {Canisters['ckBTC indexer'].principal}"
        )

    # Initialize admins if none exist
    if not Admin.instances():
        admins_to_add = set()

        # Handle multiple admins parameter
        if admin_principals:
            for principal in admin_principals:
                admins_to_add.add(principal.to_str())

        # Default to caller if no admins specified
        if not admins_to_add:
            admins_to_add.add(ic.caller().to_str())

        # Create Admin entities
        for admin_id in admins_to_add:
            logger.info(f"Adding admin principal: {admin_id}")
            Admin(_id=admin_id, principal_id=admin_id)

    if not app_data().max_results:
        new_max_results = max_results or MAX_RESULTS
        logger.info(f"Setting max results to {new_max_results}")
        app_data().max_results = new_max_results

    if not app_data().max_iteration_count:
        new_max_iteration_count = max_iteration_count or MAX_ITERATION_COUNT
        logger.info(f"Setting max iteration_count to {new_max_iteration_count}")
        app_data().max_iteration_count = new_max_iteration_count

    canister_id = ic.id().to_str()
    if not Balance[canister_id]:
        logger.info("Creating vault balance record")
        Balance(_id=canister_id, amount=0)

    logger.info(
        f"Canisters: {[canister.to_dict() for canister in Canisters.instances()]}"
    )
    admin_principals = [admin.principal_id for admin in Admin.instances()]
    logger.info(f"Admin principals: {admin_principals}")
    logger.info(f"Max results: {app_data().max_results}")
    logger.info(f"Max iteration_count: {app_data().max_iteration_count}")

    logger.info("Vault initialized.")


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # If no admins exist, allow the function to proceed
        admin_instances = Admin.instances()
        if not admin_instances:
            return func(*args, **kwargs)

        # Check if caller is admin
        caller_id = ic.caller().to_str()

        # Check if caller is in the Admin entities
        is_admin = False
        for admin in admin_instances:
            if admin.principal_id == caller_id:
                is_admin = True
                break

        if not is_admin:
            return Response(
                success=False,
                data=ResponseData(
                    Error=f"Caller ({caller_id}) is not an admin principal"
                ),
            )
        # If caller is admin, proceed with the function
        return func(*args, **kwargs)

    return wrapper


@update
@admin_only
def set_canister(canister_name: str, principal: Principal) -> Response:
    """
    Set or update the principal ID for a specific canister in the Canisters entity.

    Args:
        canister_name: The name of the canister to set/update (e.g., "ckBTC ledger", "ckBTC indexer")
        principal: The principal ID of the canister

    Returns:
        Response object with success status and message
    """

    try:
        principal_id = principal.to_str()

        logger.info(f"Setting canister '{canister_name}' to principal: {principal_id}")

        # Check if the canister already exists
        existing_canister = Canisters[canister_name]
        if existing_canister:
            # Update the existing canister record
            existing_canister.principal = principal_id
            logger.info(
                f"Updated existing canister '{canister_name}' with new principal."
            )
            return Response(
                success=True,
                data=ResponseData(
                    Message=f"Canister '{canister_name}' updated successfully"
                ),
            )
        else:
            # Create a new canister record
            Canisters(_id=canister_name, principal=principal_id)
            logger.info(f"Created new canister '{canister_name}' with principal.")
            return Response(
                success=True,
                data=ResponseData(
                    Message=f"Canister '{canister_name}' created successfully"
                ),
            )
    except Exception as e:
        logger.error(
            f"Error setting canister '{canister_name}' to principal: {e}\n{traceback.format_exc()}"
        )
        return Response(
            success=False, data=ResponseData(Error=f"Error setting canister: {str(e)}")
        )


@update
@admin_only
def transfer(to: Principal, amount: nat) -> Async[Response]:
    """
    Transfers a specified amount of tokens to a given principal.

    Args:
        to: The principal ID of the recipient
        amount: The amount of tokens to transfer

    Returns:
        Response object with success status, message, and transaction ID in the data field
    """

    try:
        if amount <= 0:
            return Response(
                success=False, data=ResponseData(Error="Amount must be positive")
            )

        logger.info(f"Transferring {amount} tokens to {to.to_str()}")
        principal = Canisters["ckBTC ledger"].principal
        ledger = ICRCLedger(Principal.from_str(principal))

        args: TransferArg = TransferArg(
            to=Account(owner=to, subaccount=None),
            amount=amount,
            fee=None,
            memo=None,
            from_subaccount=None,
            created_at_time=None,
        )

        result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

        # Handle the result
        if result.Ok is not None:
            logger.info(f"Transfer successful: {result.Ok}")
            transfer_result = result.Ok
            if transfer_result.get("Ok") is not None:
                tx_id = transfer_result["Ok"]
                return Response(
                    success=True,
                    data=ResponseData(
                        TransactionId=TransactionIdRecord(transaction_id=tx_id)
                    ),
                )
            else:
                error = transfer_result.get("Err")
                return Response(
                    success=False, data=ResponseData(Error=f"Transfer error: {error}")
                )
        else:
            logger.error(f"Transfer failed: {result.Err}")
            return Response(
                success=False, data=ResponseData(Error=f"Call error: {result.Err}")
            )
    except Exception as e:
        logger.error(f"Exception in transfer: {e}\n{traceback.format_exc()}")
        return Response(
            success=False, data=ResponseData(Error=f"Exception in transfer: {str(e)}")
        )


def _sync_status(app_data_obj):
    return (
        "Synced"
        if (
            app_data_obj.scan_end_tx_id
            == app_data_obj.scan_oldest_tx_id
            == app_data_obj.scan_start_tx_id
        )
        else "Syncing"
    )


@update
def update_transaction_history() -> Async[Response]:
    """
    Updates the transaction history for the current principal by querying the ICRC indexer
    and storing the transactions in the VaultTransaction database.

    Returns:
        Response object with success status, message, and summary data
    """
    try:
        canister_id = ic.id().to_str()
        logger.info(f"Updating transaction history for {canister_id}")

        # Get the configured indexer canister ID
        indexer_canister = Canisters["ckBTC indexer"]
        indexer_canister_id = indexer_canister.principal

        batch_max_iteration_count = app_data().max_iteration_count
        batch_max_results = app_data().max_results

        scan_end_tx_id = app_data().scan_end_tx_id
        scan_start_tx_id = app_data().scan_start_tx_id
        scan_oldest_tx_id = app_data().scan_oldest_tx_id

        batch_iteration_count = 0
        new_txs_count = 0

        # Implement cursor-based pagination to fetch all transactions
        while batch_iteration_count < batch_max_iteration_count:
            batch_iteration_count += 1
            logger.debug(
                f"batch_iteration_count: {batch_iteration_count}/{batch_max_iteration_count}"
            )

            start_tx_id = None
            if (
                scan_start_tx_id
                and scan_oldest_tx_id
                and scan_oldest_tx_id < scan_start_tx_id
            ):
                start_tx_id = scan_start_tx_id

            logger.debug(
                f"Fetching transactions with start_tx_id={start_tx_id}, max_results={batch_max_results}"
            )
            response = yield get_account_transactions(
                canister_id=indexer_canister_id,
                owner_principal=canister_id,
                start_tx_id=start_tx_id,
                max_results=batch_max_results,
            )

            if not scan_oldest_tx_id:
                scan_oldest_tx_id = response.get("oldest_tx_id")
                app_data().scan_oldest_tx_id = scan_oldest_tx_id
                logger.debug(f"scan_oldest_tx_id: {scan_oldest_tx_id}")

            response_txs = response.get("transactions")

            if not response_txs:
                logger.debug("Empty batch - No older transactions will be found")
                break

            logger.debug(f"Received {len(response_txs)} transactions")

            response_txs.sort(
                key=lambda x: x["id"], reverse=True
            )  # sort by id descending

            (
                processed_batch_oldest_tx_id,
                processed_batch_newest_tx_id,
                processed_tx_ids,
                inserted_new_txs_ids,
            ) = _process_batch_txs(canister_id, response_txs)
            logger.debug(f"Processed {len(processed_tx_ids)} transactions in batch")
            logger.debug(
                f"Processed batch oldest tx id: {processed_batch_oldest_tx_id}"
            )
            logger.debug(
                f"Processed batch newest tx id: {processed_batch_newest_tx_id}"
            )
            if not len(processed_tx_ids):
                logger.debug("No transactions processed in batch")
                break

            new_txs_count += len(inserted_new_txs_ids)

            if not scan_end_tx_id or scan_end_tx_id < processed_batch_newest_tx_id:
                scan_end_tx_id = processed_batch_newest_tx_id
                app_data().scan_end_tx_id = processed_batch_newest_tx_id
            if (
                not scan_start_tx_id
                or scan_start_tx_id > processed_batch_oldest_tx_id
                or not start_tx_id
            ):
                scan_start_tx_id = processed_batch_oldest_tx_id
                app_data().scan_start_tx_id = processed_batch_oldest_tx_id

            if processed_batch_oldest_tx_id <= scan_oldest_tx_id:
                logger.info(
                    f"Transaction history is now in sync. Latest tx id: {scan_end_tx_id}"
                )

                scan_end_tx_id = scan_end_tx_id
                scan_start_tx_id = scan_end_tx_id
                scan_oldest_tx_id = scan_end_tx_id
                app_data().scan_end_tx_id = scan_end_tx_id
                app_data().scan_start_tx_id = scan_end_tx_id
                app_data().scan_oldest_tx_id = scan_end_tx_id
                break

    except Exception as e:
        logger.error(f"Error processing transactions: {e}\n {traceback.format_exc()}")
        return Response(
            success=False,
            data=ResponseData(Error=f"Error processing transactions: {str(e)}"),
        )

    summary_msg = f"Processed a total of {new_txs_count} new transactions"
    logger.info(summary_msg)
    return Response(
        success=True,
        data=ResponseData(
            TransactionSummary=TransactionSummaryRecord(
                new_txs_count=new_txs_count,
                scan_end_tx_id=scan_end_tx_id,
                sync_status=_sync_status(app_data()),
            )
        ),
    )


def _process_batch_txs(canister_id, txs):

    processed_batch_oldest_tx_id = None
    processed_batch_newest_tx_id = None
    processed_tx_ids = []
    inserted_new_txs_ids = []

    logger.debug(f"Processing batch of {len(txs)} transactions")

    for tx in txs:
        try:
            tx_id = int(tx["id"])
            logger.debug(f"Processing transaction {tx_id}: {pformat(tx)}")

            transaction = tx["transaction"]
            timestamp = (
                int(transaction["timestamp"]) if "timestamp" in transaction else 0
            )
            kind = transaction["kind"] if "kind" in transaction else "unknown"

            # Initialize default values
            principal_from = "unknown"
            principal_to = "unknown"
            amount = 0

            # Handle different transaction types
            if kind == "mint":
                # For mint transactions, the recipient is this principal
                principal_to = canister_id
                principal_from = "mint"

                if transaction.get("mint"):
                    amount = int(transaction["mint"].get("amount", 0))

                logger.debug(
                    f"Processing mint transaction {tx_id} to {principal_to} with amount {amount}"
                )

            elif kind == "burn":
                # For burn transactions, the sender is this principal
                principal_from = canister_id
                principal_to = "burn"

                if transaction.get("burn"):
                    amount = int(transaction["burn"].get("amount", 0))

                logger.debug(
                    f"Processing burn transaction {tx_id} from {principal_from} with amount {amount}"
                )

            elif "transfer" in transaction and transaction["transfer"]:
                # Handle transfer transactions
                transfer = transaction["transfer"]

                # Get principals for from and to accounts
                principal_from = (
                    str(transfer["from_"]["owner"])
                    if "from_" in transfer and "owner" in transfer["from_"]
                    else "unknown"
                )
                principal_to = (
                    str(transfer["to"]["owner"])
                    if "to" in transfer and "owner" in transfer["to"]
                    else "unknown"
                )

                if transaction.get("transfer"):
                    amount = int(transaction["transfer"].get("amount", 0))

                logger.debug(
                    f"Processing transfer transaction {tx_id} from {principal_from} to {principal_to} with amount {amount}"
                )
            else:
                # Skip unknown transaction types
                logger.debug(
                    f"Skipping unknown transaction type: {kind} for tx {tx_id}"
                )
                continue

            logger.debug(f"Processing transaction {tx_id}")

            # Create or update the VaultTransaction
            existing_tx = VaultTransaction[tx_id]
            if existing_tx:
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

            else:
                # Create new transaction
                VaultTransaction(
                    _id=tx_id,
                    principal_from=principal_from,
                    principal_to=principal_to,
                    amount=amount,
                    timestamp=timestamp,
                    kind=kind,
                )

                # Update balances based on transaction type
                if kind == "mint":
                    # For mint, only update the recipient's balance
                    balance_to = Balance[principal_to] or Balance(
                        _id=principal_to, amount=0
                    )
                    balance_to.amount = balance_to.amount + amount
                    logger.debug(
                        f"Updated balance for {principal_to} to {balance_to.amount}"
                    )
                elif kind == "burn":
                    # For burn, only update the sender's balance
                    balance_from = Balance[principal_from] or Balance(
                        _id=principal_from, amount=0
                    )
                    balance_from.amount = balance_from.amount - amount
                    logger.debug(
                        f"Updated balance for {principal_from} to {balance_from.amount}"
                    )
                elif kind == "transfer":
                    """
                    user deposits in the vault => balance of user increases
                    vault transfers to user => balance of user decreases
                    """

                    if canister_id == principal_to:
                        balance_from = Balance[principal_from] or Balance(
                            _id=principal_from, amount=0
                        )
                        balance_from.amount = balance_from.amount + amount
                        logger.debug(
                            f"Updated balance for {principal_from} to {balance_from.amount}"
                        )

                        vault_balance = Balance[canister_id]
                        vault_balance.amount = vault_balance.amount + amount

                    if canister_id == principal_from:
                        balance_to = Balance[principal_to] or Balance(
                            _id=principal_to, amount=0
                        )
                        balance_to.amount = balance_to.amount - amount
                        logger.debug(
                            f"Updated balance for {principal_to} to {balance_to.amount}"
                        )

                        vault_balance = Balance[canister_id]
                        vault_balance.amount = vault_balance.amount - amount

                inserted_new_txs_ids.append(tx_id)

            if not processed_batch_oldest_tx_id or processed_batch_oldest_tx_id > tx_id:
                processed_batch_oldest_tx_id = tx_id
            if not processed_batch_newest_tx_id or processed_batch_newest_tx_id < tx_id:
                processed_batch_newest_tx_id = tx_id
            processed_tx_ids.append(tx_id)

        except Exception as e:
            logger.error(
                f"Error processing transaction {tx_id}: {e}\n {traceback.format_exc()}"
            )

    logger.debug(
        f"Processed {len(processed_tx_ids)} transactions, from id {processed_batch_oldest_tx_id} to id {processed_batch_newest_tx_id}"
    )
    return (
        processed_batch_oldest_tx_id,
        processed_batch_newest_tx_id,
        processed_tx_ids,
        inserted_new_txs_ids,
    )


@query
def get_balance(principal: Principal) -> Response:
    """
    Get the balance for a specific principal.

    Args:
        principal: The principal ID to check balance for

    Returns:
        Response object with success status, message, and balance data
    """
    try:
        principal_id: str = principal.to_str()

        logger.info(f"Getting balance for principal: {principal_id}")

        # Look up the balance in the database
        balance = Balance[principal_id]

        if not balance:
            return Response(
                success=False,
                data=ResponseData(
                    Error=f"Balance not found for principal: {principal_id}"
                ),
            )

        return Response(
            success=True,
            data=ResponseData(
                Balance=BalanceRecord(
                    principal_id=Principal.from_str(principal_id), amount=balance.amount
                )
            ),
        )
    except Exception as e:
        logger.error(
            f"Error getting balance for principal {principal_id}: {e}\n{traceback.format_exc()}"
        )
        return Response(
            success=False, data=ResponseData(Error=f"Error getting balance: {str(e)}")
        )


@query
def get_transactions(principal: Principal) -> Response:
    """
    Get all transactions associated with a specific principal.

    Args:
        principal: The principal ID to get transactions for

    Returns:
        Response object with success status, message, and transactions data
    """

    try:
        principal_id: str = principal.to_str()

        logger.info(f"Getting transactions for principal: {principal_id}")

        # Collect all transactions where this principal is involved
        txs = []

        for tx in VaultTransaction.instances():
            logger.debug(f"Reading stored data for transaction {tx.to_dict()}")

            # Skip transactions not related to this principal
            if tx.principal_from != principal_id and tx.principal_to != principal_id:
                continue

            amount = int(tx.amount)
            if tx.principal_to == principal_id:
                amount = -amount

            try:
                tx_record = TransactionRecord(
                    id=int(tx._id),
                    amount=amount,
                    timestamp=int(tx.timestamp),
                )
                txs.append(tx_record)
                logger.debug(f"Added transaction record: {tx_record}")
            except Exception as e:
                logger.error(f"Error creating transaction record: {e}")
                # Continue with the next transaction

        logger.info(f"Collected {len(txs)} transactions for principal {principal_id}")

        # Sort transactions by timestamp (newest first)
        if txs:
            try:
                txs.sort(key=lambda tx: tx["id"], reverse=True)
                logger.debug("Successfully sorted transactions")
            except Exception as e:
                logger.error(f"Error sorting transactions: {e}")
                # Continue without sorting if there's an error

        return Response(
            success=True,
            data=ResponseData(Transactions=txs),
        )
    except Exception as e:
        logger.error(
            f"Error getting transactions for principal {principal_id}: {e}\n {traceback.format_exc()}"
        )
        return Response(
            success=False,
            data=ResponseData(Error=f"Error getting transactions: {str(e)}"),
        )


@query
def status() -> Response:
    """
    Get statistics about the vault's state including balances and canister references.

    Returns:
        Response object with success status, message, and stats data
    """

    try:
        # Get app_data with proper typing
        app_data_obj = app_data()
        sync_status = _sync_status(app_data_obj)
        sync_tx_id = app_data_obj.scan_oldest_tx_id

        # Get all admin principals
        admin_principals = []
        for admin in Admin.instances():
            admin_principals.append(Principal.from_str(admin.principal_id))

        app_data_record = AppDataRecord(
            admin_principals=admin_principals,
            max_results=app_data_obj.max_results,
            max_iteration_count=app_data_obj.max_iteration_count,
            scan_end_tx_id=app_data_obj.scan_end_tx_id,
            scan_start_tx_id=app_data_obj.scan_start_tx_id,
            scan_oldest_tx_id=app_data_obj.scan_oldest_tx_id,
            sync_status=sync_status,
            sync_tx_id=sync_tx_id,
        )

        # Get balances with proper typing
        balances = []
        for balance in Balance.instances():
            balances.append(
                BalanceRecord(
                    principal_id=Principal.from_str(balance._id),
                    amount=balance.amount,
                )
            )

        # Get canisters with proper typing
        canisters = []
        for canister in Canisters.instances():
            canisters.append(
                CanisterRecord(
                    id=canister._id,
                    principal=Principal.from_str(canister.principal),
                )
            )

        # Create stats record
        stats = StatsRecord(
            app_data=app_data_record,
            balances=balances,
            canisters=canisters,
        )

        # Return response with stats
        return Response(
            success=True,
            data=ResponseData(Stats=stats),
        )

    except Exception as e:
        logger.error(
            f"Error retrieving vault statistics: {e}\n{traceback.format_exc()}"
        )
        return Response(
            success=False,
            data=ResponseData(Error=f"Error retrieving vault statistics: {str(e)}"),
        )


@update
@admin_only
def add_admin(new_admin: Principal) -> Response:
    """
    Add a new admin principal to the vault.

    This function can only be called by an existing admin.

    Args:
        new_admin: The principal ID of the new admin to add

    Returns:
        Response object with success status and message
    """
    try:
        new_admin_id = new_admin.to_str()

        # Check if admin already exists
        existing_admin = Admin[new_admin_id]
        if existing_admin:
            return Response(
                success=False,
                data=ResponseData(
                    Error=f"Principal {new_admin_id} is already an admin"
                ),
            )

        logger.info(f"Adding new admin principal: {new_admin_id}")

        # Create new Admin entity
        Admin(_id=new_admin_id, principal_id=new_admin_id)

        return Response(
            success=True,
            data=ResponseData(
                Message=f"Admin principal {new_admin_id} added successfully"
            ),
        )
    except Exception as e:
        logger.error(f"Error adding admin principal: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            data=ResponseData(Error=f"Error adding admin principal: {str(e)}"),
        )


@update
@admin_only
def remove_admin(admin_to_remove: Principal) -> Response:
    """
    Remove an admin principal from the vault.

    This function can only be called by an existing admin.
    Cannot remove the last admin to prevent lockout.

    Args:
        admin_to_remove: The principal ID of the admin to remove

    Returns:
        Response object with success status and message
    """
    try:
        admin_id_to_remove = admin_to_remove.to_str()

        # Check if admin exists
        admin_entity = Admin[admin_id_to_remove]
        if not admin_entity:
            return Response(
                success=False,
                data=ResponseData(
                    Error=f"Principal {admin_id_to_remove} is not an admin"
                ),
            )

        # Prevent removing the last admin
        admin_count = len(Admin.instances())
        if admin_count <= 1:
            return Response(
                success=False,
                data=ResponseData(Error="Cannot remove the last admin principal"),
            )

        logger.info(f"Removing admin principal: {admin_id_to_remove}")

        # Delete the Admin entity
        admin_entity.delete()

        return Response(
            success=True,
            data=ResponseData(
                Message=f"Admin principal {admin_id_to_remove} removed successfully"
            ),
        )
    except Exception as e:
        logger.error(f"Error removing admin principal: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            data=ResponseData(Error=f"Error removing admin principal: {str(e)}"),
        )
