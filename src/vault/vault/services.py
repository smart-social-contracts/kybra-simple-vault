from vault.utils_icp import get_transactions
from vault.entities import app_data, Transaction, Balance
import traceback
from vault.constants import TIME_PERIOD_SECONDS
from kybra import ic, Async, void
from vault.utils import log


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

    def check_transactions(self):
        log('*************** check_transactions')
        ret = []
        if not app_data().last_processed_index:
            get_transactions_response = yield get_transactions(0, 1)
            log('*************** get_transactions_response', get_transactions_response)
            log_length = get_transactions_response['log_length']
            app_data().last_processed_index = log_length
            return ret

        get_transactions_response = yield get_transactions(app_data().last_processed_index, 100)
        transactions = get_transactions_response['transactions']

        for i, transaction in enumerate(transactions):
            transaction_index = app_data().last_processed_index

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
            except:
                print(traceback.format_exc())

            app_data().last_processed_index = app_data().last_processed_index + 1
            if not app_data().first_processed_index:
                app_data().first_processed_index = transaction_index

            return ret
