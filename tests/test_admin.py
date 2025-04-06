import unittest
from unittest.mock import MagicMock, patch

from src.vault.vault.admin import (
    reset,
    set_admin,
    set_heartbeat_interval_seconds,
    set_ledger_canister,
)
from src.vault.vault.entities import app_data, ledger_canister


class TestAdmin(unittest.TestCase):
    def setUp(self):
        # Set up mock for IC environment
        self.reset_mock = patch("src.vault.vault.admin.services.reset").start()

        # Mock any other dependencies as needed
        patch("src.vault.vault.admin.logger").start()

    def tearDown(self):
        patch.stopall()

    def test_admin_can_set_admin(self):
        # Mock app_data
        app_data_mock = MagicMock()
        app_data_mock.admin_principal = "admin-principal"
        patch("src.vault.vault.admin.app_data", return_value=app_data_mock).start()

        # Call set_admin with admin caller
        set_admin("admin-principal", "new-admin-principal")

        # Verify admin principal was changed
        self.assertEqual(app_data_mock.admin_principal, "new-admin-principal")

    def test_non_admin_cannot_set_admin(self):
        # Mock app_data
        app_data_mock = MagicMock()
        app_data_mock.admin_principal = "admin-principal"
        patch("src.vault.vault.admin.app_data", return_value=app_data_mock).start()

        # Call set_admin with non-admin caller and expect exception
        with self.assertRaises(ValueError):
            set_admin("non-admin-principal", "new-admin-principal")

        # Verify admin principal was not changed
        self.assertEqual(app_data_mock.admin_principal, "admin-principal")

    def test_admin_can_reset(self):
        # Mock app_data
        app_data_mock = MagicMock()
        app_data_mock.admin_principal = "admin-principal"
        patch("src.vault.vault.admin.app_data", return_value=app_data_mock).start()

        # Call reset with admin caller
        reset("admin-principal")

        # Verify reset was called
        self.reset_mock.assert_called_once()

    def test_non_admin_cannot_reset(self):
        # Mock app_data
        app_data_mock = MagicMock()
        app_data_mock.admin_principal = "admin-principal"
        patch("src.vault.vault.admin.app_data", return_value=app_data_mock).start()

        # Call reset with non-admin caller and expect exception
        with self.assertRaises(ValueError):
            reset("non-admin-principal")

        # Verify reset was not called
        self.reset_mock.assert_not_called()

    def test_admin_can_set_heartbeat_interval_seconds(self):
        # Mock app_data
        app_data_mock = MagicMock()
        app_data_mock.admin_principal = "admin-principal"
        patch("src.vault.vault.admin.app_data", return_value=app_data_mock).start()

        # Call set_heartbeat_interval_seconds with admin caller
        set_heartbeat_interval_seconds("admin-principal", 60)

        # Verify heartbeat interval was changed
        self.assertEqual(app_data_mock.heartbeat_interval_seconds, 60)

    def test_non_admin_cannot_set_heartbeat_interval_seconds(self):
        # Mock app_data
        app_data_mock = MagicMock()
        app_data_mock.admin_principal = "admin-principal"
        app_data_mock.heartbeat_interval_seconds = 30
        patch("src.vault.vault.admin.app_data", return_value=app_data_mock).start()

        # Call set_heartbeat_interval_seconds with non-admin caller and expect exception
        with self.assertRaises(ValueError):
            set_heartbeat_interval_seconds("non-admin-principal", 60)

        # Verify heartbeat interval was not changed
        self.assertEqual(app_data_mock.heartbeat_interval_seconds, 30)

    def test_admin_can_set_ledger_canister(self):
        # Mock app_data
        app_data_mock = MagicMock()
        app_data_mock.admin_principal = "admin-principal"
        patch("src.vault.vault.admin.app_data", return_value=app_data_mock).start()

        # Create a mock ledger canister
        ledger_canister_mock = MagicMock()
        ledger_canister_mock.principal = "old-principal"
        patch(
            "src.vault.vault.admin.ledger_canister", return_value=ledger_canister_mock
        ).start()

        # Create a new principal
        new_principal = "new-ledger-canister-principal"

        # Call set_ledger_canister with admin caller
        set_ledger_canister("admin-principal", "new-ledger-canister-id", new_principal)

        # Verify ledger canister was changed
        self.assertEqual(
            ledger_canister_mock.principal,
            "new-ledger-canister-principal",
        )

    def test_non_admin_cannot_set_ledger_canister(self):
        # Create a new principal
        new_principal = "new-ledger-canister-principal"

        # Mock app_data to return an admin principal that is different from our caller
        app_data_mock = MagicMock()
        app_data_mock.admin_principal = (
            "admin-principal"  # This is different from "non-admin-principal"
        )
        patch("src.vault.vault.admin.app_data", return_value=app_data_mock).start()

        # Create a mock ledger canister with initial value
        ledger_canister_mock = MagicMock()
        ledger_canister_mock.principal = "admin-principal"
        patch(
            "src.vault.vault.admin.ledger_canister", return_value=ledger_canister_mock
        ).start()

        # Call set_ledger_canister with non-admin caller and expect exception
        with self.assertRaises(ValueError):
            set_ledger_canister(
                "non-admin-principal", "new-ledger-canister-id", new_principal
            )

        # Verify ledger canister was not changed
        self.assertEqual(
            ledger_canister_mock.principal,
            "admin-principal",
        )


if __name__ == "__main__":
    unittest.main()
