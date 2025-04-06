import unittest
from unittest.mock import MagicMock, patch

from vault.entities import Balance, VaultTransaction, app_data
from vault.services import TransactionTracker, reset


def run():
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
    return 0


class TestReset(unittest.TestCase):
    def setUp(self):
        # Set up mock for IC environment
        self.ic_mock = patch("vault.services.ic").start()
        # Add some test data
        app_data().log_length = 100
        app_data().last_processed_index = 50
        app_data().vault_principal = "vault-principal"

        # Create some test transactions and balances
        VaultTransaction(
            _id="1",
            principal_from="sender",
            principal_to="vault-principal",
            amount=1000,
            timestamp=123456789,
            kind="deposit",
        )

        Balance(_id="sender", amount=-1000)
        Balance(_id="vault-principal", amount=1000)

    def tearDown(self):
        patch.stopall()

    def test_reset(self):
        # Verify we have data before reset
        self.assertEqual(len(list(VaultTransaction.instances())), 1)
        self.assertEqual(len(list(Balance.instances())), 2)

        # Run the reset function
        reset()

        # Verify all data is cleared
        self.assertEqual(len(list(VaultTransaction.instances())), 0)
        self.assertEqual(len(list(Balance.instances())), 0)
