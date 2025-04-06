import unittest
from unittest.mock import MagicMock, patch
from vault.services import TransactionTracker
from vault.entities import app_data

def run():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    return 0

class TestSyncRecovery(unittest.TestCase):
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
        
    def test_recover_from_out_of_sync(self):
        # Mock a response where first_index is ahead of our last_processed_index
        mock_response = MagicMock()
        mock_response.Ok = {
            "log_length": 110,
            "transactions": [],  # No transactions in the response
            "first_index": 60    # Our last_processed_index was 50, so we're out of sync
        }
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response
        
        # Run the method under test
        tracker = TransactionTracker()
        tracker.check_transactions()
        
        # Verify we advanced to the first_index from the ledger
        self.assertEqual(app_data().last_processed_index, 60)
        self.assertEqual(app_data().log_length, 110)
