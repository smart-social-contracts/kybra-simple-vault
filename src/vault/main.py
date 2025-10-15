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
    TestModeRecord,
    TransactionIdRecord,
    TransactionRecord,
    TransactionSummaryRecord,
    TransferArg,
    TransferResult,
)
from vault.constants import CANISTER_PRINCIPALS, MAX_ITERATION_COUNT, MAX_RESULTS
from vault.entities import (
    Balance,
    Canisters,
    VaultTransaction,
    app_data,
    test_mode_data,
)
from vault.ic_util_calls import get_account_transactions, set_account_mock_transaction

logger = get_logger(__name__)

storage = StableBTreeMap[str, str](memory_id=1, max_key_size=100, max_value_size=1000)
Database.init(db_storage=storage)


@init
def init_(
    canisters: Opt[Vec[Tuple[str, Principal]]] = None,
    admin_principal: Opt[Principal] = None,
    max_results: Opt[nat] = None,
    max_iteration_count: Opt[nat] = None,
    test_mode_enabled: Opt[bool] = False,
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
        new_max_iteration_count = (
            max_iteration_count if max_iteration_count else MAX_ITERATION_COUNT
        )
        logger.info(f"Setting max iteration_count to {new_max_iteration_count}")
        app_data().max_iteration_count = new_max_iteration_count

    if test_mode_enabled is not None:
        logger.info(f"Setting test mode to {test_mode_enabled}")
        test_mode_data().test_mode_enabled = test_mode_enabled

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

    if test_mode_data().test_mode_enabled:
        logger.info(f"Test mode active: {test_mode_data().test_mode_enabled}")

    logger.info("Vault initialized.")


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if caller is admin
        caller_id = ic.caller().to_str()
        admin_id = app_data().admin_principal
        if caller_id != admin_id:
            return Response(
                success=False,
                data=ResponseData(
                    Error=f"Caller ({caller_id}) is not the admin principal ({admin_id})"
                ),
            )
        # If caller is admin, proceed with the function
        return func(*args, **kwargs)

    return wrapper


def test_mode_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not test_mode_data().test_mode_enabled:
            return Response(
                success=False,
                data=ResponseData(Error="Test mode is not enabled"),
            )
        # If test mode is enabled, proceed with the function
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

        if test_mode_data().test_mode_enabled:
            # Create a mock transaction record for testing
            tx_id = test_mode_data().tx_id
            test_mode_data().tx_id += 1

            # Create mock transaction record
            from kybra import ic

            timestamp = ic.time()
            VaultTransaction(
                _id=str(tx_id),
                principal_from=ic.id().to_str(),
                principal_to=to.to_str(),
                amount=amount,
                timestamp=timestamp,
                kind="mock_transfer",
            )

            # Update balances for mock transaction
            from_balance = Balance[ic.id().to_str()] or Balance(
                _id=ic.id().to_str(), amount=0
            )
            to_balance = Balance[to.to_str()] or Balance(_id=to.to_str(), amount=0)

            from_balance.amount -= amount
            to_balance.amount += amount

            return Response(
                success=True,
                data=ResponseData(
                    TransactionId=TransactionIdRecord(transaction_id=tx_id)
                ),
            )

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

        if test_mode_data().test_mode_enabled:
            return Response(
                success=True,
                data=ResponseData(
                    Message="Test mode enabled, skipping update_transaction_history"
                ),
            )

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

        # If no balance record exists, default to 0 (don't create a record)
        balance_amount = balance.amount if balance else 0

        return Response(
            success=True,
            data=ResponseData(
                Balance=BalanceRecord(
                    principal_id=Principal.from_str(principal_id), amount=balance_amount
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
            if tx.principal_from == principal_id:
                amount = -amount  # Negative for sender (outgoing)
            # Positive for recipient (incoming) - no change needed

            try:
                tx_record = TransactionRecord(
                    id=int(tx._id),
                    amount=amount,
                    timestamp=int(tx.timestamp),
                    principal_from=Principal.from_str(tx.principal_from),
                    principal_to=Principal.from_str(tx.principal_to),
                    kind=tx.kind,
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

        app_data_record = AppDataRecord(
            admin_principal=Principal.from_str(app_data_obj.admin_principal),
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
            data=ResponseData(
                Error=f"Error retrieving vault statistics: {traceback.format_exc()}"
            ),
        )


@query
def test_mode_status() -> Response:
    """
    Get data about the vault's test mode state.

    Returns:
        Response object with success status, message, and test mode data
    """

    try:
        # Get app_data with proper typing
        test_mode_data_obj = test_mode_data()

        test_mode_record = TestModeRecord(
            test_mode_enabled=test_mode_data_obj.test_mode_enabled,
            tx_id=test_mode_data_obj.tx_id,
        )

        # Return response with stats
        return Response(
            success=True,
            data=ResponseData(TestMode=test_mode_record),
        )

    except Exception as e:
        logger.error(f"Error retrieving test mode data: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            data=ResponseData(
                Error=f"Error retrieving test mode data: {traceback.format_exc()}"
            ),
        )


@update
@admin_only
def set_admin(new_admin: Principal) -> Response:
    """
    Set a new admin principal for the vault.

    This function can only be called by the current admin.

    Args:
        new_admin: The principal ID of the new admin

    Returns:
        Response object with success status and message
    """
    try:
        current_admin = app_data().admin_principal
        new_admin_id = new_admin.to_str()

        logger.info(f"Changing admin principal from {current_admin} to {new_admin_id}")

        # Update the admin_principal in app_data
        app_data().admin_principal = new_admin_id

        return Response(
            success=True,
            data=ResponseData(
                Message=f"Admin principal updated successfully to {new_admin_id}"
            ),
        )
    except Exception as e:
        logger.error(f"Error setting admin principal: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            data=ResponseData(Error=f"Error setting admin principal: {str(e)}"),
        )


@update
@test_mode_only
def test_mode_set_mock_transaction(
    principal_from: Principal,
    principal_to: Principal,
    amount: nat,
    kind: Opt[str] = None,
    timestamp: Opt[nat] = None,
) -> Response:
    try:
        logger.info(
            f"Setting mock transaction from {principal_from} to {principal_to}, amount: {amount}"
        )

        # Use default value if kind is not provided
        actual_kind = kind if kind is not None else "mock_transfer"
        
        set_account_mock_transaction(
            principal_from.to_str(), principal_to.to_str(), amount, actual_kind, timestamp
        )
        return Response(
            success=True,
            data=ResponseData(Message="Mock transaction set successfully"),
        )
    except Exception as e:
        logger.error(f"Error setting mock transaction: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            data=ResponseData(Error=f"Error setting mock transaction: {str(e)}"),
        )


@update
@test_mode_only
def test_mode_set_balance(principal: Principal, amount: nat) -> Response:
    """
    Set a specific balance for a principal in test mode.

    Args:
        principal: The principal to set balance for
        amount: The balance amount to set

    Returns:
        Response object with success status and message
    """
    try:
        principal_id = principal.to_str()
        logger.info(f"Setting test mode balance for {principal_id} to {amount}")

        # Create or update balance
        balance = Balance[principal_id] or Balance(_id=principal_id, amount=0)
        balance.amount = amount

        return Response(
            success=True,
            data=ResponseData(Message=f"Balance set to {amount} for {principal_id}"),
        )
    except Exception as e:
        logger.error(f"Error setting test mode balance: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            data=ResponseData(Error=f"Error setting test mode balance: {str(e)}"),
        )


@update
@test_mode_only
def test_mode_reset() -> Response:
    """
    Reset test mode state (clear transactions and balances).

    Returns:
        Response object with success status and message
    """
    try:

        logger.info("Resetting test mode state")

        # Reset transaction ID
        test_mode_data().tx_id = 0

        # Clear all transactions
        for tx in VaultTransaction.instances():
            if tx.kind == "mock_transfer":
                tx.delete()

        # Reset all balances to 0
        for balance in Balance.instances():
            balance.amount = 0

        return Response(
            success=True,
            data=ResponseData(Message="Test mode state reset successfully"),
        )
    except Exception as e:
        logger.error(f"Error resetting test mode: {e}\n{traceback.format_exc()}")
        return Response(
            success=False,
            data=ResponseData(Error=f"Error resetting test mode: {str(e)}"),
        )
