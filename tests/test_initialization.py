import unittest
from unittest.mock import MagicMock, patch

from vault.entities import app_data
from vault.services import TransactionTracker


def run():
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
    return 0


class TestInitialization(unittest.TestCase):
    def setUp(self):
        # Set up mock for IC environment
        self.ic_mock = patch("vault.services.ic").start()
        self.get_transactions_mock = patch("vault.services.get_transactions").start()
        self.principal_mock = patch("src.vault.main.Principal").start()
        
        # Reset app_data to ensure clean state for each test
        app_data().log_length = 0
        app_data().last_processed_index = None
        app_data().ledger_canister_id = None
        app_data().ledger_canister_principal = None
        app_data().admin_principal = None
        app_data().vault_principal = None
        app_data().heartbeat_interval_seconds = 0

    def tearDown(self):
        patch.stopall()

    def test_initialize_tracker(self):
        # Set required values for canister initialization
        app_data().ledger_canister_principal = "ledger-principal"
        app_data().vault_principal = "vault-principal"
        
        # Mock the response from get_transactions
        mock_response = MagicMock()
        mock_response.Ok = {"log_length": 100, "transactions": []}
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response

        # Run the method under test
        tracker = TransactionTracker()
        tracker.check_transactions()

        # Verify initialization happened correctly
        self.assertEqual(app_data().log_length, 100)
        self.assertIsNone(app_data().last_processed_index)

        # Check that get_transactions was called with correct parameters
        self.get_transactions_mock.assert_called_once_with(0, 1)
        
    def test_tracker_with_missing_ledger_principal(self):
        """Test TransactionTracker behavior when ledger_canister_principal is None."""
        # Explicitly set ledger_canister_principal to None
        app_data().ledger_canister_principal = None
        app_data().vault_principal = "vault-principal"
        
        # Mock the response from get_transactions
        mock_response = MagicMock()
        mock_response.Ok = {"log_length": 100, "transactions": []}
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response
        
        # Executing check_transactions should raise an AttributeError
        # when ledger_canister_principal is None
        with self.assertRaises(Exception):
            tracker = TransactionTracker()
            tracker.check_transactions()
            
    def test_tracker_with_missing_vault_principal(self):
        """Test TransactionTracker behavior when vault_principal is None."""
        # Set up with ledger_principal but missing vault_principal
        app_data().ledger_canister_principal = "ledger-principal"
        app_data().vault_principal = None
        
        # Mock the response from get_transactions
        mock_response = MagicMock()
        mock_response.Ok = {"log_length": 100, "transactions": []}
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response
        
        # Executing check_transactions should raise an exception 
        # when vault_principal is missing
        with self.assertRaises(Exception):
            tracker = TransactionTracker()
            tracker.check_transactions()
            
    def test_check_transactions_with_defensive_handling(self):
        """Test how the system handles potentially None values."""
        # Set up the test with minimal required values
        app_data().ledger_canister_principal = "ledger-principal"
        app_data().vault_principal = "vault-principal"
        
        # Mock the response from get_transactions
        mock_response = MagicMock()
        mock_response.Ok = {"log_length": 100, "transactions": []}
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response
        
        # Run the method under test - should complete without exceptions
        tracker = TransactionTracker()
        tracker.check_transactions()
        
        # Verify expected state
        self.assertEqual(app_data().log_length, 100)
            
    def test_initialization_with_error_response(self):
        """Test tracker initialization when get_transactions returns an error."""
        # Set required values
        app_data().ledger_canister_principal = "ledger-principal"
        app_data().vault_principal = "vault-principal"
        
        # Mock an error response from get_transactions
        mock_response = MagicMock()
        mock_response.Ok = None
        mock_response.Err = {"error": "Some error occurred"}
        self.get_transactions_mock.return_value = mock_response

        # Run initialization
        tracker = TransactionTracker()
        tracker.check_transactions()

        # Verify state didn't change on error
        self.assertEqual(app_data().log_length, 0)
        self.assertIsNone(app_data().last_processed_index)
