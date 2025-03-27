from vault.utils_icp import get_transactions
from vault.entities import app_data, Transaction, Balance
import traceback
from vault.constants import TIME_PERIOD_SECONDS
from kybra import ic
from vault.utils import log


def transactions_tracker_hearbeat():
    ic.print('transactions_tracker_hearbeat')
    now = ic.time()
    ic.print('now = %s' % now)
    if app_data().last_heartbeat_time is None:
        app_data().last_heartbeat_time = 0
    ic.print('last_heartbeat_time = %s' % app_data().last_heartbeat_time)
    if (now - app_data().last_heartbeat_time) / 1e9 > TIME_PERIOD_SECONDS:
        try:
            ic.print('check_transactions')
            app_data().last_heartbeat_time = now
            TransactionTracker().check_transactions()
        except:
            ic.print(traceback.format_exc())
    ic.print('transactions_tracker_hearbeat end')


class TransactionTracker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TransactionTracker, cls).__new__(cls)
        return cls._instance

    def check_transactions(self):
        if not app_data().last_processed_index:
            get_transactions_response = get_transactions(0, 1)
            log_length = get_transactions_response['log_length']
            app_data().last_processed_index = log_length
            return

        get_transactions_response = get_transactions(app_data().last_processed_index, 100)
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
            except:
                print(traceback.format_exc())

            app_data().last_processed_index = app_data().last_processed_index + 1
            if not app_data().first_processed_index:
                app_data().first_processed_index = transaction_index
