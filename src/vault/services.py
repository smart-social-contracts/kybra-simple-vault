from entities import ApplicationData, Transaction, Category
from utils import parse_candid

class TransactionTrackerService:
    _instance = None

    def __new__(cls):
        if cls.__instance__ is None:
            cls._instance = super(TransactionTrackerService, cls).__new__(cls)
            cls._instance.app_data = ApplicationData.get_instance()
        return cls._instance

    def check_transactions(self):
        if not self.app_data.log_length:
            # TODO: get the latest log_length
        
        

