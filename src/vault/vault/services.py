from vault.utils_icp import get_transactions
from vault.entities import app_data, Transaction, Balance
import traceback
from vault.constants import TIME_PERIOD_SECONDS, TRANSACTION_BATCH_SIZE
from kybra import ic, Async, void, update, query


from kybra_simple_logging import get_logger

logger = get_logger(__name__)
logger.set_level(logger.DEBUG)


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


class TransactionTracker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TransactionTracker, cls).__new__(cls)
        return cls._instance

    def check_transactions(self) -> Async[str]:
        logger.debug('*************** check_transactions')
        ret = []
        if not app_data().log_length:
            get_transactions_response = yield get_transactions(0, 1)
            logger.debug('*************** get_transactions_response (0) = %s' % get_transactions_response)
            app_data().log_length = get_transactions_response['log_length']
            return app_data().to_dict()

        get_transactions_response = yield get_transactions(app_data().log_length, TRANSACTION_BATCH_SIZE)
        logger.debug('*************** get_transactions_response (1) = %s' % get_transactions_response)
        
        transaction_index = app_data().log_length
        log_length = get_transactions_response['log_length']
        app_data().log_length = log_length
        transactions = get_transactions_response['transactions']

        for i, transaction in enumerate(transactions):
            try:
                principal_from = transaction['transfer']['from']['owner']
                principal_to = transaction['transfer']['to']['owner']
                relevant = app_data().vault_principal in (principal_from, principal_to)
                if relevant:
                    amount = int(transaction['transfer']['amount'])
                    t = Transaction(_id=str(transaction_index),
                                    principal_from=principal_from,
                                    principal_to=principal_to,
                                    amount=amount,
                                    timestamp=transaction['timestamp'],
                                    kind=transaction['kind'])
                    balance_from = Balance[principal_from] or Balance(_id=principal_from)
                    balance_to = Balance[principal_to] or Balance(_id=principal_to)
                    balance_from.amount = balance_from.amount - amount
                    balance_to.amount = balance_to.amount + amount
                    ret.append(t._id)
            except Exception as e:
                logger.error("Error processing transaction %s: %s" % (transaction, str(e)))
                logger.error(traceback.format_exc())

            transaction_index += 1

        app_data().last_processed_index = transaction_index
        return str(log_length - transaction_index - 1)


@update
def check_transactions_update() -> Async[str]:
    return TransactionTracker().check_transactions()
