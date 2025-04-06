import traceback

from kybra import Async, CallResult, ic, query, update, void
from kybra_simple_db import *
from kybra_simple_logging import get_logger

from vault.candid_types import (
    GetTransactionsRequest,
    GetTransactionsResponse,
    ICRCLedger,
    Transaction,
)
from vault.constants import CKBTC_CANISTER, TRANSACTION_BATCH_SIZE
from vault.entities import Balance, VaultTransaction, app_data
from vault.utils import get_nested
from vault.utils_icp import get_transactions

logger = get_logger(__name__)
logger.set_level(logger.DEBUG)


def reset() -> void:
    Database.get_instance().clear()


class TransactionTracker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TransactionTracker, cls).__new__(cls)
        return cls._instance

    def check_transactions(self) -> Async[int]:
        logger.debug("Starting transaction check")
        ret = []
        if not app_data().log_length:
            logger.debug("Transaction history tracking not initialized")
            # get_transactions_response = yield get_transactions(0, 1)
            response: CallResult[GetTransactionsResponse] = yield get_transactions(0, 1)
            # Log after the first yield to ensure it's captured
            logger.debug("Checking transactions - initializing log tracking")
            if response.Err:
                logger.error("Error getting transactions: %s" % response.Err)
                raise Exception(response.Err)

            app_data().log_length = response.Ok["log_length"]
            logger.debug("log_length initialized to %s" % response.Ok["log_length"])
            return 0

        # Log after we know we're going to do the actual transaction check
        logger.debug(
            "Checking transactions - processing from index %s"
            % (app_data().last_processed_index or app_data().log_length)
        )
        requested_index = app_data().last_processed_index or app_data().log_length
        response: CallResult[GetTransactionsResponse] = yield get_transactions(
            requested_index, TRANSACTION_BATCH_SIZE
        )
        if response.Err:
            logger.error("Error getting transactions: %s" % response.Err)
            raise Exception(response.Err)

        transaction_index = requested_index - 1
        log_length = response.Ok["log_length"]
        app_data().log_length = log_length
        transactions = response.Ok["transactions"]

        if response.Ok["first_index"] > requested_index and not transactions:
            logger.warning(
                "ckBTC ledger canister's history is ahead of our last processed index. Some transactions may have been missed. Setting transaction_index to %s"
                % response.Ok["first_index"])

            transaction_index = response.Ok["first_index"]
        else:
            logger.debug("Fetched %s transactions" % len(transactions))

            for transaction in transactions:
                logger.debug(
                    "Processing transaction %s:\n%s" % (transaction_index, transaction)
                )
                try:
                    principal_from = get_nested(
                        transaction, "transfer", "from_", "owner"
                    )
                    principal_to = get_nested(transaction, "transfer", "to", "owner")
                    relevant = app_data().vault_principal in (
                        principal_from,
                        principal_to,
                    )
                    if relevant:
                        amount = int(get_nested(transaction, "transfer", "amount"))
                        t = VaultTransaction(
                            _id=str(transaction_index),
                            principal_from=principal_from,
                            principal_to=principal_to,
                            amount=amount,
                            timestamp=get_nested(transaction, "transfer", "timestamp"),
                            kind=get_nested(transaction, "transfer", "kind"),
                        )
                        balance_from = Balance[principal_from] or Balance(
                            _id=principal_from
                        )
                        balance_to = Balance[principal_to] or Balance(_id=principal_to)
                        balance_from.amount = balance_from.amount - amount
                        balance_to.amount = balance_to.amount + amount
                        ret.append(t._id)
                        logger.debug(
                            "Stored transaction %s (amount=%s, from=%s, to=%s)"
                            % (t._id, amount, principal_from, principal_to)
                        )
                except Exception as e:
                    logger.error(
                        "Error processing transaction %s: %s" % (transaction, str(e))
                    )
                    logger.error(traceback.format_exc())

                transaction_index += 1

        app_data().last_processed_index = transaction_index
        logger.debug("Last processed transaction index set to %s" % transaction_index)
        num_transactions_pending_check = log_length - transaction_index - 1
        logger.debug("%s transactions pending check" % (num_transactions_pending_check))
        return num_transactions_pending_check
