import traceback
from pprint import pformat
from functools import wraps

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
from kybra_simple_logging import get_logger, set_log_level, Level

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
    TransactionsListRecord,
    TransferArg,
    TransferResult,
)
from vault.constants import CANISTER_PRINCIPALS, MAX_ITERATIONS, MAX_RESULTS
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
    max_iterations: Opt[nat] = None,
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

    if not app_data().max_iterations:
        new_max_iterations = max_iterations or MAX_ITERATIONS
        logger.info(f"Setting max iterations to {new_max_iterations}")
        app_data().max_iterations = new_max_iterations

    logger.info(
        f"Canisters: {[canister.to_dict() for canister in Canisters.instances()]}"
    )
    logger.info(f"Admin principal: {app_data().admin_principal}")
    logger.info(f"Max results: {app_data().max_results}")
    logger.info(f"Max iterations: {app_data().max_iterations}")

    logger.info("Vault initialized.")


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if caller is admin
        if ic.caller().to_str() != app_data().admin_principal:
            return Response(
                success=False,
                message="Caller is not the admin principal",
                data=None
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
                data=None
            )
        else:
            # Create a new canister record
            Canisters(_id=canister_name, principal=principal_id.to_str())
            logger.info(f"Created new canister '{canister_name}' with principal.")
            return Response(
                success=True,
                message=f"Created new canister '{canister_name}' with principal.",
                data=None
            )
    except Exception as e:
        logger.error(
            f"Error setting canister '{canister_name}' to principal: {e}\n{traceback.format_exc()}"
        )
        return Response(
            success=False,
            message=f"Error setting canister: {str(e)}",
            data=None
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
                success=False,
                message="Caller is not the admin principal",
                data=None
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
            if transfer_result.get('Ok') is not None:
                tx_id = transfer_result['Ok']
                return Response(
                    success=True,
                    message=f"Transfer successful with transaction ID: {tx_id}",
                    data=ResponseData(TransactionId=TransactionIdRecord(transaction_id=tx_id))
                )
            else:
                error = transfer_result.get('Err')
                return Response(
                    success=False,
                    message=f"Transfer error: {error}",
                    data=None
                )
        else:
            logger.error(f"Transfer failed: {result.Err}")
            return Response(
                success=False,
                message=f"Call error: {result.Err}",
                data=None
            )
    except Exception as e:
        logger.error(f"Exception in transfer: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            message=f"Exception in transfer: {str(e)}",
            data=None
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
        principal_id = ic.id().to_str()
        logger.debug(f"Updating transaction history for {principal_id}")

        # Get the configured indexer canister ID
        indexer_canister = Canisters["ckBTC indexer"]
        indexer_canister_id = indexer_canister.principal

        # Initialize variables to store all transactions and track pagination
        all_transactions = []
        has_more = True
        current_start = None
        iterations = 0
        max_iterations = (
            app_data().max_iterations
        )  # Limit pagination to prevent excessive calls
        max_results = (
            app_data().max_results
        )  # Limit pagination to prevent excessive calls

        # Implement cursor-based pagination to fetch all transactions
        while has_more and iterations < max_iterations:
            # Log the current request parameters
            logger.debug(
                f"Fetching transactions with start={current_start}, max_results={max_results}"
            )

            # Query the indexer for transactions using the current cursor position
            response = yield get_account_transactions(
                canister_id=indexer_canister_id,
                owner_principal=principal_id,
                start_tx_id=current_start,
                max_results=max_results,
            )

            # Check if we received a valid response with transactions
            if (
                not response
                or "transactions" not in response
                or not response["transactions"]
            ):
                logger.debug(f"No more transactions found at cursor {current_start}")
                has_more = False
                break

            # Collect the transactions from this batch
            batch_transactions = response["transactions"]
            all_transactions.extend(batch_transactions)
            logger.debug(
                f"Received {len(batch_transactions)} transactions, total now: {len(all_transactions)}"
            )

            # Check if we got fewer transactions than requested - means we've reached the end
            if len(batch_transactions) < max_results:
                logger.debug(
                    f"Received fewer transactions than requested ({len(batch_transactions)} < {max_results})"
                )
                has_more = False
                break

            # Get the oldest transaction ID to use as the next cursor
            oldest_tx_id = response.get("oldest_tx_id")
            if oldest_tx_id is None:
                logger.debug("No oldest_tx_id in response, pagination complete")
                has_more = False
                break

            logger.debug(f"batch_transactions = {batch_transactions}")
            tx_id_oldest = batch_transactions[-1]["id"]

            logger.debug(f"tx_id_oldest = {tx_id_oldest}")
            logger.debug(
                f"app_data().last_transaction_id = {app_data().last_transaction_id}"
            )

            # take the the oldest tx id received (not oldest_tx_id) but, if that tx id was already processed, break
            if (
                app_data().last_transaction_id
                and tx_id_oldest > app_data().last_transaction_id
            ):
                logger.debug(
                    f"continuing pagination loop, setting current_start to {tx_id_oldest}"
                )
                current_start = tx_id_oldest
                iterations += 1
            else:
                has_more = False
                break

            logger.debug(
                f"Next cursor will be {current_start}, iteration {iterations}/{max_iterations}"
            )

        # Update the response to use the aggregated transactions
        if all_transactions:
            response["transactions"] = all_transactions
            if "balance" in response:
                logger.debug(f"Balance found in response: {response['balance']}")

        logger.debug(f"Response: {response}")

        # Check if we have transactions in the response
        has_transactions = "transactions" in response and response["transactions"]

        if not response or not has_transactions:
            return Response(
                success=False,
                message=f"No transactions found for principal {principal_id}",
                data=None
            )

        # Track new and updated transactions
        new_count = 0
        updated_count = 0

        # Process each transaction and update the database
        transactions = sorted(response["transactions"], key=lambda x: x["id"])
        for tx in transactions:
            try:
                logger.debug(f"Processing transaction {tx['id']}: {pformat(tx)}")

                # Extract transaction data using dictionary access
                tx_id = str(tx["id"])
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
                    principal_to = principal_id
                    principal_from = "mint"

                    if transaction.get("mint"):
                        amount = int(transaction["mint"].get("amount", 0))

                    logger.debug(
                        f"Processing mint transaction {tx_id} to {principal_to} with amount {amount}"
                    )

                elif kind == "burn":
                    # For burn transactions, the sender is this principal
                    principal_from = principal_id
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
                        kind=kind,
                    )
                    new_count += 1

                    # Update balances based on transaction type
                    some_balance_update = False
                    if kind == "mint":
                        # For mint, only update the recipient's balance
                        balance_to = Balance[principal_to] or Balance(
                            _id=principal_to, amount=0
                        )
                        balance_to.amount = balance_to.amount + amount
                        some_balance_update = True
                        logger.debug(
                            f"Updated balance for {principal_to} to {balance_to.amount}"
                        )
                    elif kind == "burn":
                        # For burn, only update the sender's balance
                        balance_from = Balance[principal_from] or Balance(
                            _id=principal_from, amount=0
                        )
                        balance_from.amount = balance_from.amount - amount
                        some_balance_update = True
                        logger.debug(
                            f"Updated balance for {principal_from} to {balance_from.amount}"
                        )
                    elif kind == "transfer":
                        """
                        user deposits in the vault => balance of user increases
                        vault transfers to user => balance of user decreases
                        """

                        if principal_id == principal_to:
                            balance_from = Balance[principal_from] or Balance(
                                _id=principal_from, amount=0
                            )
                            balance_from.amount = balance_from.amount + amount
                            some_balance_update = True
                            logger.debug(
                                f"Updated balance for {principal_from} to {balance_from.amount}"
                            )

                        if principal_id == principal_from:
                            balance_to = Balance[principal_to] or Balance(
                                _id=principal_to, amount=0
                            )
                            balance_to.amount = balance_to.amount - amount
                            some_balance_update = True
                            logger.debug(
                                f"Updated balance for {principal_to} to {balance_to.amount}"
                            )

                    logger.debug(f"Setting last_transaction_id to {tx_id}")
                    app_data().last_transaction_id = tx_id

                    logger.info(
                        f"Processed transaction {tx_id}: kind={kind}, amount={amount}, from={principal_from}, to={principal_to}"
                    )
                    if not some_balance_update:
                        logger.warning(f"No balance updates for transaction {tx_id}")

            except Exception as e:
                logger.error(
                    f"Error processing transaction {tx_id}: {e}\n {traceback.format_exc()}"
                )

        summary_msg = f"Processed {len(transactions)} transactions: {new_count} new, {updated_count} updated"
        return Response(
            success=True,
            message=summary_msg,
            data=ResponseData(TransactionSummary=TransactionSummaryRecord(
                total_processed=len(transactions),
                new_count=new_count,
                updated_count=updated_count
            ))
        )
    except Exception as e:
        logger.error(f"Error processing transactions: {e}\n {traceback.format_exc()}")
        return Response(
            success=False,
            message=f"Error processing transactions: {str(e)}",
            data=None
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

        # Return the balance amount or 0 if not found
        amount = balance.amount if balance else 0

        return Response(
            success=True,
            message=f"Balance retrieved for principal: {principal_id}",
            data=ResponseData(Balance=BalanceRecord(
                principal_id=principal_id,
                amount=amount)
            )
        )
    except Exception as e:
        logger.error(f"Error getting balance for principal {principal_id}: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            message=f"Error getting balance: {str(e)}",
            data=None
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
                txs.sort(key=lambda tx: tx['id'], reverse=True)
                logger.debug("Successfully sorted transactions")
            except Exception as e:
                logger.error(f"Error sorting transactions: {e}")
                # Continue without sorting if there's an error

        return Response(
            success=True,
            message=f"Retrieved {len(txs)} transactions for principal: {principal_id}",
            data=ResponseData(Transactions=txs)
        )
    except Exception as e:
        logger.error(
            f"Error getting transactions for principal {principal_id}: {e}\n {traceback.format_exc()}"
        )
        return Response(
            success=False,
            message=f"Error getting transactions: {str(e)}",
            data=None
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
            last_transaction_id=app_data_obj.last_transaction_id,
            max_results=app_data_obj.max_results,
            max_iterations=app_data_obj.max_iterations,
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
            data=ResponseData(Stats=stats)
        )

    except Exception as e:
        logger.error(
            f"Error retrieving vault statistics: {e}\n{traceback.format_exc()}"
        )
        return Response(
            success=False,
            message=f"Error retrieving vault statistics: {str(e)}",
            data=None
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
