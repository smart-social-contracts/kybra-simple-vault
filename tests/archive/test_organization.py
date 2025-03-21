import pytest
from pathlib import Path
import json

from test_utils import check
from ggg.utils import IGNORE_TAG

# Constants
THIS_DIR = Path(__file__).parent
SCENARIOS_DIR = THIS_DIR / "scenarios"

class TestOrganization:
    """Test suite for organization member functionality"""
    
    def test_create_organization(self, dfx_command):
        """Test creating a new organization"""
        command = dfx_command + ["create_organization", "test_org", "Test Organization"]
        expected = {
            'id': 'test_org',
            'description': 'Test Organization',
            'type': 'Organization',
            'creator': IGNORE_TAG,
            'owner': IGNORE_TAG,
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'updater': IGNORE_TAG
        }
        result = subprocess.run(command, capture_output=True, text=True)
        assert check(command, result.stdout, expected) == 0

    def test_add_member(self, dfx_command):
        """Test adding a member to an organization"""
        # Create member organization
        member_command = dfx_command + ["create_organization", "member_org", "Member Organization"]
        subprocess.run(member_command, capture_output=True, text=True)
        
        # Add member to organization
        command = dfx_command + ["add_member", "test_org", "member_org"]
        expected = {'status': 'ok'}
        result = subprocess.run(command, capture_output=True, text=True)
        assert check(command, result.stdout, expected) == 0
        
        # Verify member was added
        check_command = dfx_command + ["has_member", "test_org", "member_org"]
        expected = True
        result = subprocess.run(check_command, capture_output=True, text=True)
        assert check(check_command, result.stdout, expected) == 0
        
        # Verify token balance
        balance_command = dfx_command + ["get_token_balance", "test_org", "member_org"]
        expected = 1
        result = subprocess.run(balance_command, capture_output=True, text=True)
        assert check(balance_command, result.stdout, expected) == 0

    def test_has_member_non_member(self, dfx_command):
        """Test has_member returns False for non-members"""
        # Create non-member organization
        non_member_command = dfx_command + ["create_organization", "non_member", "Non-Member Organization"]
        subprocess.run(non_member_command, capture_output=True, text=True)
        
        # Check membership
        command = dfx_command + ["has_member", "test_org", "non_member"]
        expected = False
        result = subprocess.run(command, capture_output=True, text=True)
        assert check(command, result.stdout, expected) == 0

    def test_multiple_members(self, dfx_command):
        """Test adding multiple members to an organization"""
        # Create member organizations
        for i in range(3):
            member_command = dfx_command + ["create_organization", f"member_{i}", f"Member Organization {i}"]
            subprocess.run(member_command, capture_output=True, text=True)
            
            # Add member
            add_command = dfx_command + ["add_member", "test_org", f"member_{i}"]
            expected = {'status': 'ok'}
            result = subprocess.run(add_command, capture_output=True, text=True)
            assert check(add_command, result.stdout, expected) == 0
            
            # Verify membership
            check_command = dfx_command + ["has_member", "test_org", f"member_{i}"]
            expected = True
            result = subprocess.run(check_command, capture_output=True, text=True)
            assert check(check_command, result.stdout, expected) == 0
            
            # Verify token balance
            balance_command = dfx_command + ["get_token_balance", "test_org", f"member_{i}"]
            expected = 1
            result = subprocess.run(balance_command, capture_output=True, text=True)
            assert check(balance_command, result.stdout, expected) == 0
