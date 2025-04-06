import unittest
from unittest.mock import MagicMock, patch
from vault.services import TransactionTracker
from vault.entities import app_data, VaultTransaction, Balance

def run():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    return 0

class TestBalanceTracking(unittest.TestCase):
    def setUp(self):
        # Set up mock for IC environment
        self.ic_mock = patch('vault.services.ic').start()
        self.get_transactions_mock = patch('vault.services.get_transactions').start()
        # Initialize app_data with test values
        app_data().log_length = 100
        app_data().last_processed_index = 50
        app_data().vault_principal = "vault-principal"
        
    def tearDown(self):
        patch.stopall()
        
    def test_balance_update_on_deposit(self):
        # Create a mock deposit transaction
        mock_transaction = {
            "transfer": {
                "from_": {"owner": "sender-principal"},
                "to": {"owner": "vault-principal"},
                "amount": "1000",
                "timestamp": 123456789,
                "kind": "deposit"
            }
        }
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.Ok = {
            "log_length": 110,
            "transactions": [mock_transaction],
            "first_index": 50
        }
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response
        
        # Run the method under test
        tracker = TransactionTracker()
        tracker.check_transactions()
        
        # Verify balances were updated correctly
        sender_balance = Balance["sender-principal"]
        vault_balance = Balance["vault-principal"]
        
        self.assertEqual(sender_balance.amount, -1000)  # Sender sent 1000
        self.assertEqual(vault_balance.amount, 1000)   # Vault received 1000
        
    def test_balance_update_on_withdrawal(self):
        # Create a mock withdrawal transaction
        mock_transaction = {
            "transfer": {
                "from_": {"owner": "vault-principal"},
                "to": {"owner": "receiver-principal"},
                "amount": "500",
                "timestamp": 123456789,
                "kind": "withdrawal"
            }
        }
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.Ok = {
            "log_length": 110,
            "transactions": [mock_transaction],
            "first_index": 50
        }
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response
        
        # Run the method under test
        tracker = TransactionTracker()
        tracker.check_transactions()
        
        # Verify balances were updated correctly
        vault_balance = Balance["vault-principal"]
        receiver_balance = Balance["receiver-principal"]
        
        self.assertEqual(vault_balance.amount, -500)    # Vault sent 500
        self.assertEqual(receiver_balance.amount, 500)  # Receiver got 500
