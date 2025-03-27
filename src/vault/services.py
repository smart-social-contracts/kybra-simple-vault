import utils_icp
import utils
from entities import app_data, Transaction


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
            cls._instance.reset()
        return cls._instance

    def reset(self, vault_principal: str):
        app_data.vault_principal = vault_principal
        app_data.log_length = 0
        app_data.balance = 0  # TODO: add support for initial default values in kybra-simple-db
        app_data.total_inflow = 0
        app_data.total_outflow = 0
        app_data.initial_index = 0

    def check_transactions(self):
        get_transactions_response = utils_icp.get_transactions(app_data.log_length, 100)
        transactions = get_transactions_response['transactions']
        first_index = get_transactions_response['first_index']

        for i, transaction in enumerate(transactions):
            transaction_index = first_index + i
            if not app_data.initial_index:
                app_data.initial_index = transaction_index
            t = Transaction(_id=transaction_index,
                            principal_from=transaction['transfer']['from']['owner'],
                            principal_to=transaction['transfer']['to']['owner'],
                            amount=transaction['transfer']['amount'],
                            timestamp=transaction['timestamp'],
                            kind=transaction['kind'],
                            )
            # TODO: add categories

        app_data.log_length = get_transactions_response['log_length']
        print('** app_data', app_data.to_dict())



