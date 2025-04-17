import unittest
from unittest.mock import MagicMock, patch

from vault.entities import Balance, VaultTransaction, app_data
from vault.services import TransactionTracker


def run():
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
    return 0


class TestTransactionProcessing(unittest.TestCase):
    def setUp(self):
        # Set up mock for IC environment
        self.ic_mock = patch("vault.services.ic").start()
        self.get_transactions_mock = patch("vault.services.get_transactions").start()
        
        # Initialize app_data with test values
        app_data().log_length = 100
        app_data().last_processed_index = 50
        app_data().vault_principal = "vault-principal"
        app_data().ledger_canister_principal = "ledger-principal"
        app_data().ledger_canister_id = "ledger-id"

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
                "kind": "deposit",
            }
        }

        # Mock the response from get_transactions
        mock_response = MagicMock()
        mock_response.Ok = {
            "log_length": 110,
            "transactions": [mock_transaction],
            "first_index": 50,
        }
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response

        # Run the method under test
        tracker = TransactionTracker()
        tracker.check_transactions()

        # Verify transaction was processed
        self.assertEqual(app_data().log_length, 110)
        self.assertEqual(app_data().last_processed_index, 51)

        # Check that the transaction was stored
        transactions = list(VaultTransaction.instances())
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].principal_from, "sender-principal")
        self.assertEqual(transactions[0].principal_to, "vault-principal")
        self.assertEqual(transactions[0].amount, 1000)
        
    def test_check_transactions_with_no_new_transactions(self):
        """Test when there are no new transactions to process."""
        # Mock a response with no new transactions
        mock_response = MagicMock()
        mock_response.Ok = {
            "log_length": 100,  # Same as current log_length
            "transactions": [],
            "first_index": 50,
        }
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response

        # Run the method under test
        tracker = TransactionTracker()
        tracker.check_transactions()

        # Verify no change in log_length or last_processed_index
        self.assertEqual(app_data().log_length, 100)
        self.assertEqual(app_data().last_processed_index, 50)
        
        # Verify no transactions were stored
        transactions = list(VaultTransaction.instances())
        self.assertEqual(len(transactions), 0)
        
    def test_check_transactions_with_invalid_transaction_format(self):
        """Test handling of transactions with invalid format."""
        # Create a mock transaction with invalid format
        mock_transaction = {
            "invalid_format": "This is not a valid transaction"
        }

        # Mock the response
        mock_response = MagicMock()
        mock_response.Ok = {
            "log_length": 110,
            "transactions": [mock_transaction],
            "first_index": 50,
        }
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response

        # Run the method under test - should handle invalid format gracefully
        tracker = TransactionTracker()
        tracker.check_transactions()

        # Verify log_length updated even if transaction wasn't processed
        self.assertEqual(app_data().log_length, 110)
        self.assertEqual(app_data().last_processed_index, 51)
        
        # Invalid transaction shouldn't be stored
        transactions = list(VaultTransaction.instances())
        self.assertEqual(len(transactions), 0)
        
    def test_check_transactions_with_error_response(self):
        """Test handling of error responses from get_transactions."""
        # Mock an error response
        mock_response = MagicMock()
        mock_response.Ok = None
        mock_response.Err = {"error": "Some error occurred"}
        self.get_transactions_mock.return_value = mock_response

        # Run the method under test
        tracker = TransactionTracker()
        tracker.check_transactions()

        # Verify no change in state on error
        self.assertEqual(app_data().log_length, 100)
        self.assertEqual(app_data().last_processed_index, 50)
        
    def test_check_transactions_with_multiple_transactions(self):
        """Test processing multiple transactions at once."""
        # Create multiple mock transactions
        mock_transactions = [
            {
                "transfer": {
                    "from_": {"owner": "sender1-principal"},
                    "to": {"owner": "vault-principal"},
                    "amount": "1000",
                    "timestamp": 123456789,
                    "kind": "deposit",
                }
            },
            {
                "transfer": {
                    "from_": {"owner": "vault-principal"},
                    "to": {"owner": "receiver-principal"},
                    "amount": "500",
                    "timestamp": 123456790,
                    "kind": "withdrawal",
                }
            },
            {
                "transfer": {
                    "from_": {"owner": "sender2-principal"},
                    "to": {"owner": "vault-principal"},
                    "amount": "2000",
                    "timestamp": 123456791,
                    "kind": "deposit",
                }
            }
        ]

        # Mock the response
        mock_response = MagicMock()
        mock_response.Ok = {
            "log_length": 110,
            "transactions": mock_transactions,
            "first_index": 50,
        }
        mock_response.Err = None
        self.get_transactions_mock.return_value = mock_response

        # Run the method under test
        tracker = TransactionTracker()
        tracker.check_transactions()

        # Verify all transactions were processed
        self.assertEqual(app_data().log_length, 110)
        self.assertEqual(app_data().last_processed_index, 53)
        
        # Verify all transactions were stored
        transactions = list(VaultTransaction.instances())
        self.assertEqual(len(transactions), 3)
