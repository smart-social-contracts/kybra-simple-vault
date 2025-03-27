import utils_icp
import utils
from entities import app_data, Transaction, Balance
import traceback

def transactions_tracker_hearbeat():
    # ic.print("this runs ~1 time per second")
    now = ic.time()
    if (now - app_data.last_heartbeat_time) / 1e9 > TIME_PERIOD_SECONDS:
        app_data.last_heartbeat_time = now
        TransactionTracker().check_transactions()

class TransactionTracker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TransactionTracker, cls).__new__(cls)
        return cls._instance

    def check_transactions(self):
        if not app_data.last_processed_index:
            get_transactions_response = utils_icp.get_transactions(0, 1)
            log_length = get_transactions_response['log_length']
            app_data.last_processed_index = log_length
            return

        get_transactions_response = utils_icp.get_transactions(app_data.last_processed_index, 100)
        transactions = get_transactions_response['transactions']
        
        for i, transaction in enumerate(transactions):
            transaction_index = app_data.last_processed_index
            print('transaction %d' % transaction_index)

            try:
                principal_from = transaction['transfer']['from']['owner']
                principal_to = transaction['transfer']['to']['owner']
                relevant = app_data.vault_principal in (principal_from, principal_to)
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

            app_data.last_processed_index = app_data.last_processed_index + 1
            if not app_data.first_processed_index:
                app_data.first_processed_index = transaction_index

