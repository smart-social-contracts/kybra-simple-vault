import unittest
from unittest.mock import MagicMock, patch
from vault.services import TransactionTracker
from vault.entities import app_data, VaultTransaction, Balance

def run():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    return 0

class TestTransactionProcessing(unittest.TestCase):
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
        
    def test_check_transactions(self):
        # Create a mock transaction that should be processed
        mock_transaction = {
            "transfer": {
                "from_": {"owner": "sender-principal"},
                "to": {"owner": "vault-principal"},
                "amount": "1000",
                "timestamp": 123456789,
                "kind": "deposit"
            }
        }
        
        # Mock the response from get_transactions
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
        pending_count = tracker.check_transactions()
        
        # Verify transaction was processed
        self.assertEqual(app_data().log_length, 110)
        self.assertEqual(app_data().last_processed_index, 51)
        
        # Check that the transaction was stored
        transactions = list(VaultTransaction.instances())
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].principal_from, "sender-principal")
        self.assertEqual(transactions[0].principal_to, "vault-principal")
        self.assertEqual(transactions[0].amount, 1000)
