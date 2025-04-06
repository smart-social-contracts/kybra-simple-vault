import unittest
from unittest.mock import MagicMock, patch
from vault.admin import set_admin, reset, set_heartbeat_interval_seconds
from vault.entities import app_data

def run():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    return 0

class TestAdmin(unittest.TestCase):
    def setUp(self):
        # Set up mock for IC environment
        self.reset_mock = patch('vault.vault.admin.services.reset').start()
        
        # Mock any other dependencies as needed
        patch('vault.vault.admin.logger').start()
        
        # Set up admin
        app_data().admin_principal = "admin-principal"
        
    def tearDown(self):
        patch.stopall()
        
    def test_admin_can_set_admin(self):
        # Create a new principal
        new_principal = "new-admin-principal"
        
        # Call set_admin with admin caller
        set_admin("admin-principal", new_principal)
        
        # Verify admin was changed
        self.assertEqual(app_data().admin_principal, "new-admin-principal")
        
    def test_non_admin_cannot_set_admin(self):
        # Create a new principal
        new_principal = "new-admin-principal"
        
        # Call set_admin with non-admin caller and expect exception
        with self.assertRaises(ValueError):
            set_admin("non-admin-principal", new_principal)
            
        # Verify admin was not changed
        self.assertEqual(app_data().admin_principal, "admin-principal")
        
    def test_admin_can_reset(self):
        # Call reset with admin caller
        reset("admin-principal")
        
        # Verify reset was called
        self.reset_mock.assert_called_once()
        
    def test_non_admin_cannot_reset(self):
        # Call reset with non-admin caller and expect exception
        with self.assertRaises(ValueError):
            reset("non-admin-principal")
            
        # Verify reset was not called
        self.reset_mock.assert_not_called()