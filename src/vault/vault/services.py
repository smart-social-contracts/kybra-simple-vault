from vault.utils_icp import get_transactions
from vault.entities import app_data, VaultTransaction, Balance
import traceback
from vault.constants import TIME_PERIOD_SECONDS, TRANSACTION_BATCH_SIZE
from kybra import ic, Async, void, update, query, CallResult
from kybra_simple_db import *
from vault.candid_types import (
    Account,
    TransferArg,
    GetTransactionsRequest,
    ICRCLedger,
    GetTransactionsResult,
    GetTransactionsResponse,
    Transaction
)

from kybra_simple_logging import get_logger

logger = get_logger(__name__)


def transactions_tracker_hearbeat() -> Async[void]:
    if TIME_PERIOD_SECONDS <= 0:
        return

    now = ic.time()
    if not app_data().last_heartbeat_time or (now - app_data().last_heartbeat_time) / 1e9 > TIME_PERIOD_SECONDS:
        try:
            app_data().last_heartbeat_time = now
            yield TransactionTracker().check_transactions()
        except:
            ic.print(traceback.format_exc())


def reset() -> void:
    Database.get_instance().clear()


class TransactionTracker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TransactionTracker, cls).__new__(cls)
        return cls._instance

    def check_transactions(self) -> Async[int]:
        logger.debug("Checking transactions")
        ret = []
        if not app_data().log_length:
            logger.debug("Transaction history tracking not initialized")
            # get_transactions_response = yield get_transactions(0, 1)
            response: CallResult[GetTransactionsResponse] = yield get_transactions(0, 1)
            if response.Err:
                logger.error("Error getting transactions: %s" % response.Err)
                raise Exception(response.Err)

            app_data().log_length = response.Ok['log_length']
            logger.debug("log_length initialized to %s" % response.Ok['log_length'])
            return 0

        requested_index = app_data().last_processed_index or app_data().log_length
        response: CallResult[GetTransactionsResponse] = yield get_transactions(requested_index, TRANSACTION_BATCH_SIZE)
        if response.Err:
            logger.error("Error getting transactions: %s" % response.Err)
            raise Exception(response.Err)

        transaction_index = requested_index - 1
        log_length = response.Ok['log_length']
        app_data().log_length = log_length
        transactions = response.Ok['transactions']
        logger.debug("Fetched %s transactions" % len(transactions))

        for transaction in transactions:
            logger.debug("Processing transaction %s:\n%s" % (transaction_index, transaction))
            try:
                principal_from = transaction['transfer']['from']['owner']
                principal_to = transaction['transfer']['to']['owner']
                relevant = app_data().vault_principal in (principal_from, principal_to)
                if relevant:
                    amount = int(transaction['transfer']['amount'])
                    t = VaultTransaction(_id=str(transaction_index),
                                         principal_from=principal_from,
                                         principal_to=principal_to,
                                         amount=amount,
                                         timestamp=transaction['transfer']['timestamp'],
                                         kind=transaction['transfer']['kind'])
                    balance_from = Balance[principal_from] or Balance(_id=principal_from)
                    balance_to = Balance[principal_to] or Balance(_id=principal_to)
                    balance_from.amount = balance_from.amount - amount
                    balance_to.amount = balance_to.amount + amount
                    ret.append(t._id)
                    logger.debug("Stored transaction %s (amount=%s, from=%s, to=%s)" % (t._id, amount, principal_from, principal_to))
            except Exception as e:
                logger.error("Error processing transaction %s: %s" % (transaction, str(e)))
                logger.error(traceback.format_exc())

            transaction_index += 1

        app_data().last_processed_index = transaction_index
        logger.debug("Last processed transaction index set to %s" % transaction_index)
        num_transactions_pending_check = log_length - transaction_index - 1
        logger.debug("%s transactions pending check" % (num_transactions_pending_check))
        return num_transactions_pending_check
