

class TransactionTracker:
    def __init__(self, my_principal: str, initial_log_length: int):
        self.my_principal = my_principal
        self.log_length = initial_log_length
        self.balance = 0

    def check_transactions(self):
        '''
        1. call
