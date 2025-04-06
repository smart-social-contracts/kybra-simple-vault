import unittest
from unittest.mock import MagicMock, patch
from vault.services import TransactionTracker
from vault.entities import app_data

def run():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    return 0

class TestInitialization(unittest.TestCase):
    def setUp(self):
        # Set up mock for IC environment
        self.ic_mock = patch('vault.services.ic').start()
        self.get_transactions_mock = patch('vault.services.get_transactions').start()
        # Reset app_data
        app_data().log_length = 0
        app_data().last_processed_index = None
        
    def tearDown(self):
        patch.stopall()
        
    def test_initialize_tracker(self):
        # Mock the response from get_transactions
        mock_response = MagicMock()
        mock_response.Ok = {"log_length": 100, "transactions": []}
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response
        
        # Run the method under test
        tracker = TransactionTracker()
        result = tracker.check_transactions()
        
        # Verify initialization happened correctly
        self.assertEqual(app_data().log_length, 100)
        self.assertIsNone(app_data().last_processed_index)
        
        # Check that get_transactions was called with correct parameters
        self.get_transactions_mock.assert_called_once_with(0, 1)
