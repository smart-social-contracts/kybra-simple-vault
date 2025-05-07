import traceback
from functools import wraps
from pprint import pformat

from kybra import (
    Async,
    CallResult,
    Opt,
    Principal,
    Record,
    StableBTreeMap,
    Tuple,
    Vec,
    ic,
    init,
    match,
    nat,
    query,
    update,
    void,
)
from kybra_simple_db import Database
from kybra_simple_logging import Level, get_logger, set_log_level

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
    TransactionsListRecord,
    TransactionSummaryRecord,
    TransferArg,
    TransferResult,
)
from vault.constants import CANISTER_PRINCIPALS, MAX_RESULTS, MAX_iteration_count
from vault.entities import Balance, Canisters, VaultTransaction, app_data
from vault.ic_util_calls import get_account_transactions

logger = get_logger(__name__)
set_log_level(Level.DEBUG, logger_name=logger.name)

storage = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100000, max_value_size=1000
)
Database.init(db_storage=storage, audit_enabled=True)

# TODO: can this be called by anyone? CHECK


@init
def init_(
    canisters: Opt[Vec[Tuple[str, Principal]]] = None,
    admin_principal: Opt[Principal] = None,
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

    if not app_data().admin_principal:
        new_admin_principal = (
            admin_principal.to_str() if admin_principal else ic.caller().to_str()
        )
        logger.info(f"Setting admin principal to {new_admin_principal}")
        app_data().admin_principal = new_admin_principal

    if not app_data().max_results:
        new_max_results = max_results or MAX_RESULTS
        logger.info(f"Setting max results to {new_max_results}")
        app_data().max_results = new_max_results

    if not app_data().max_iteration_count:
        new_max_iteration_count = max_iteration_count or MAX_iteration_count
        logger.info(f"Setting max iteration_count to {new_max_iteration_count}")
        app_data().max_iteration_count = new_max_iteration_count

    canister_id = ic.id().to_str()
    if not Balance[canister_id]:
        logger.info("Creating vault balance record")
        Balance(_id=canister_id, amount=0)

    logger.info(
        f"Canisters: {[canister.to_dict() for canister in Canisters.instances()]}"
    )
    logger.info(f"Admin principal: {app_data().admin_principal}")
    logger.info(f"Max results: {app_data().max_results}")
    logger.info(f"Max iteration_count: {app_data().max_iteration_count}")

    logger.info("Vault initialized.")


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if caller is admin
        if ic.caller().to_str() != app_data().admin_principal:
            return Response(
                success=False, message="Caller is not the admin principal", data=None
            )
        # If caller is admin, proceed with the function
        return func(*args, **kwargs)

    return wrapper


@update
@admin_only
def set_canister(canister_name: str, principal_id: Principal) -> Response:
    """
    Set or update the principal ID for a specific canister in the Canisters entity.

    Args:
        canister_name: The name of the canister to set/update (e.g., "ckBTC ledger", "ckBTC indexer")
        principal_id: The principal ID of the canister

    Returns:
        Response object with success status and message
    """

    try:
        logger.info(
            f"Setting canister '{canister_name}' to principal: {principal_id.to_str()}"
        )

        # Check if the canister already exists
        existing_canister = Canisters[canister_name]
        if existing_canister:
            # Update the existing canister record
            existing_canister.principal = principal_id.to_str()
            logger.info(
                f"Updated existing canister '{canister_name}' with new principal."
            )
            return Response(
                success=True,
                message=f"Updated existing canister '{canister_name}' with new principal.",
                data=None,
            )
        else:
            # Create a new canister record
            Canisters(_id=canister_name, principal=principal_id.to_str())
            logger.info(f"Created new canister '{canister_name}' with principal.")
            return Response(
                success=True,
                message=f"Created new canister '{canister_name}' with principal.",
                data=None,
            )
    except Exception as e:
        logger.error(
            f"Error setting canister '{canister_name}' to principal: {e}\n{traceback.format_exc()}"
        )
        return Response(
            success=False, message=f"Error setting canister: {str(e)}", data=None
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
        logger.debug(f"Transfer called by {ic.caller()}")
        logger.debug(f"Admin principal is {app_data().admin_principal}")
        if ic.caller().to_str() != app_data().admin_principal:
            return Response(
                success=False, message="Caller is not the admin principal", data=None
            )

        if amount <= 0:
            return Response(success=False, message="Amount must be positive", data=None)
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
                    message=f"Transfer successful with transaction ID: {tx_id}",
                    data=ResponseData(
                        TransactionId=TransactionIdRecord(transaction_id=tx_id)
                    ),
                )
            else:
                error = transfer_result.get("Err")
                return Response(
                    success=False, message=f"Transfer error: {error}", data=None
                )
        else:
            logger.error(f"Transfer failed: {result.Err}")
            return Response(
                success=False, message=f"Call error: {result.Err}", data=None
            )
    except Exception as e:
        logger.error(f"Exception in transfer: {e}\n{traceback.format_exc()}")
        return Response(
            success=False, message=f"Exception in transfer: {str(e)}", data=None
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
        logger.debug(f"Updating transaction history for {canister_id}")

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
                scan_start_tx_id is not None
                and scan_oldest_tx_id is not None
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

            # if len(response_txs) < batch_max_results:
            #     logger.debug(f"Number of transactions in batch is less than max_results ({len(response_txs)} < {batch_max_results})")
            #     do_not_iterate_next = False

            response_txs.sort(
                key=lambda x: x["id"], reverse=True
            )  # sort by id descending

            # highest_tx_id = response_txs[0]["id"]
            # if scan_oldest_tx_id is not None and scan_oldest_tx_id == scan_start_tx_id and highest_tx_id <= scan_end_tx_id:
            #     logger.info("No new transactions to be scanned. We are in sync.")
            #     break

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
                or start_tx_id is None
            ):
                scan_start_tx_id = processed_batch_oldest_tx_id
                app_data().scan_start_tx_id = processed_batch_oldest_tx_id

            if processed_batch_oldest_tx_id <= scan_oldest_tx_id:
                logger.debug("Transaction history is now in sync")

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
            success=False, message=f"Error processing transactions: {str(e)}", data=None
        )

    summary_msg = f"Processed a total of {new_txs_count} new transactions"
    logger.info(summary_msg)
    return Response(
        success=True,
        message=summary_msg,
        data=ResponseData(
            TransactionSummary=TransactionSummaryRecord(
                new_txs_count=new_txs_count,
            )
        ),
    )


def _process_batch_txs(canister_id, txs):

    processed_batch_oldest_tx_id = None
    processed_batch_newest_tx_id = None
    processed_tx_ids = []
    inserted_new_txs_ids = []

    logger.debug(f"Processing batch of {len(txs)} transactions")

    # txs.sort(key=lambda x: x["id"], reverse=True)  # sort by id descending

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
def get_balance(principal_id: str) -> Response:
    """
    Get the balance for a specific principal.

    Args:
        principal_id: The principal ID to check balance for

    Returns:
        Response object with success status, message, and balance data
    """
    try:
        logger.debug(f"Getting balance for principal: {principal_id}")

        # Look up the balance in the database
        balance = Balance[principal_id]

        if not balance:
            return Response(
                success=False,
                message=f"Balance not found for principal: {principal_id}",
                data=None,
            )

        return Response(
            success=True,
            message=f"Balance retrieved for principal: {principal_id}",
            data=ResponseData(
                Balance=BalanceRecord(principal_id=principal_id, amount=balance.amount)
            ),
        )
    except Exception as e:
        logger.error(
            f"Error getting balance for principal {principal_id}: {e}\n{traceback.format_exc()}"
        )
        return Response(
            success=False, message=f"Error getting balance: {str(e)}", data=None
        )


@query
def get_transactions(principal_id: str) -> Response:
    """
    Get all transactions associated with a specific principal.

    Args:
        principal_id: The principal ID to get transactions for

    Returns:
        Response object with success status, message, and transactions data
    """

    try:
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
            message=f"Retrieved {len(txs)} transactions for principal: {principal_id}",
            data=ResponseData(Transactions=txs),
        )
    except Exception as e:
        logger.error(
            f"Error getting transactions for principal {principal_id}: {e}\n {traceback.format_exc()}"
        )
        return Response(
            success=False, message=f"Error getting transactions: {str(e)}", data=None
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
        app_data_record = AppDataRecord(
            admin_principal=app_data_obj.admin_principal,
            max_results=app_data_obj.max_results,
            max_iteration_count=app_data_obj.max_iteration_count,
            scan_end_tx_id=app_data_obj.scan_end_tx_id,
            scan_start_tx_id=app_data_obj.scan_start_tx_id,
            scan_oldest_tx_id=app_data_obj.scan_oldest_tx_id,
        )

        # Get balances with proper typing
        balances = []
        for balance in Balance.instances():
            balances.append(
                BalanceRecord(
                    principal_id=balance._id,
                    amount=balance.amount,
                )
            )

        # Get canisters with proper typing
        canisters = []
        for canister in Canisters.instances():
            canisters.append(
                CanisterRecord(
                    _id=canister._id,
                    principal=canister.principal,
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
            message="Vault statistics retrieved successfully",
            data=ResponseData(Stats=stats),
        )

    except Exception as e:
        logger.error(
            f"Error retrieving vault statistics: {e}\n{traceback.format_exc()}"
        )
        return Response(
            success=False,
            message=f"Error retrieving vault statistics: {str(e)}",
            data=None,
        )


# ##### Import Kybra and the internal function #####


from kybra import Opt, Record, Vec, nat, query  # noqa: E402
from kybra_simple_logging import get_canister_logs as _get_canister_logs  # noqa: E402


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
        logger_name=logger_name,
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


@update
def execute_code(code: str) -> str:
    """Executes Python code and returns the output.

    This is the core function needed for the Kybra Simple Shell to work.
    It captures stdout, stderr, and return values from the executed code.
    """
    import io
    import sys
    import traceback

    stdout = io.StringIO()
    stderr = io.StringIO()
    sys.stdout = stdout
    sys.stderr = stderr

    try:
        # Try to evaluate as an expression
        result = eval(code, globals())
        if result is not None:
            ic.print(repr(result))
    except SyntaxError:
        try:
            # If it's not an expression, execute it as a statement
            # Use the built-in exec function but with a different name to avoid conflict
            exec_builtin = exec
            exec_builtin(code, globals())
        except Exception:
            traceback.print_exc()
    except Exception:
        traceback.print_exc()

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    return stdout.getvalue() + stderr.getvalue()
