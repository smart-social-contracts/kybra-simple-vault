import utils_icp
import utils
from entities import app_data, Transaction


class TransactionTracker:
    def __init__(self, vault_principal: str, log_length: int = 0):
        app_data.log_length = log_length
        app_data.vault_principal = vault_principal

    def check_transactions(self):
        get_transactions_response = utils_icp.get_transactions(app_data.log_length, 100)
        transactions = get_transactions_response['transactions']

        for transaction in transactions:
            t = Transaction(principal_from=transaction['transfer']['from']['owner'],
                            principal_to=transaction['transfer']['to']['owner'],
                            amount=transaction['transfer']['amount'],
                            timestamp=transaction['timestamp'],
                            categories=transaction['categories'])

        app_data.log_length = app_data.log_length or 0 + len(transactions)
        print('** app_data', app_data.to_dict())



