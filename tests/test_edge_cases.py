import unittest
from unittest.mock import MagicMock, patch

# Import from the same paths used by other test files
from vault.entities import app_data
from vault.services import TransactionTracker


def run():
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
    return 0


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        # Set up mock for IC environment
        self.ic_mock = patch("vault.services.ic").start()
        self.get_transactions_mock = patch("vault.services.get_transactions").start()
        
        # Reset app_data before each test
        app_data().log_length = 0
        app_data().last_processed_index = None
        app_data().ledger_canister_id = None
        app_data().ledger_canister_principal = None
        app_data().admin_principal = None
        app_data().vault_principal = None
        app_data().heartbeat_interval_seconds = 0

    def tearDown(self):
        patch.stopall()

    def test_check_transactions_with_missing_ledger_principal(self):
        """Test check_transactions behavior when ledger_canister_principal is None."""
        # Explicitly set ledger_canister_principal to None
        app_data().ledger_canister_principal = None
        
        # Mock the ic.caller() to return a valid principal
        caller_mock = MagicMock()
        caller_mock.to_str.return_value = "caller-principal"
        self.ic_mock.caller.return_value = caller_mock
        
        # Expect an AttributeError when check_transactions is called
        with self.assertRaises(AttributeError):
            # Call directly or via TransactionTracker as appropriate
            tracker = TransactionTracker()
            tracker.check_transactions()
            
    def test_check_transactions_with_missing_vault_principal(self):
        """Test check_transactions behavior when vault_principal is None."""
        # Set up valid ledger principal but missing vault_principal
        app_data().ledger_canister_principal = "ledger-principal"
        app_data().vault_principal = None
        
        # Mock the ic.caller() to return a valid principal
        caller_mock = MagicMock()
        caller_mock.to_str.return_value = "caller-principal"
        self.ic_mock.caller.return_value = caller_mock
        
        # Expect an exception when check_transactions is called
        with self.assertRaises(Exception):
            tracker = TransactionTracker()
            tracker.check_transactions()
            
    def test_initialization_with_all_none_values(self):
        """Test initialization with all optional parameters set to None."""
        # This test verifies the system can handle all None values at init
        # Note: actual init behavior should be tested separately if possible

        # Set all values to None
        app_data().ledger_canister_id = None
        app_data().ledger_canister_principal = None
        app_data().admin_principal = None
        app_data().vault_principal = None
        
        # Mock a successful response from get_transactions to isolate test
        mock_response = MagicMock()
        mock_response.Ok = {"log_length": 0, "transactions": []}
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response
        
        # Expect AttributeError due to missing principal
        with self.assertRaises(AttributeError):
            tracker = TransactionTracker()
            tracker.check_transactions()
            
    def test_check_transactions_with_error_response(self):
        """Test handling of error responses from get_transactions."""
        # Set valid principals
        app_data().ledger_canister_principal = "ledger-principal"
        app_data().vault_principal = "vault-principal"
        
        # Mock an error response
        mock_response = MagicMock()
        mock_response.Ok = None
        mock_response.Err = {"error": "Some error message"}
        self.get_transactions_mock.return_value = mock_response
        
        # Run the method - it should handle errors gracefully
        tracker = TransactionTracker()
        # This should not raise an exception if error handling is correct
        tracker.check_transactions()
        
        # Verify the log_length did not change
        self.assertEqual(app_data().log_length, 0)
