import os
import sys
import pytest
from pathlib import Path
from pytest import mark

from test_utils import check
from ggg.user import User, UserGroup
from ggg.organization import Organization
from ggg.wallet import Wallet
from ggg.token import Token
from ggg.base import initialize


class TestGGG:
    """Test suite for GGG framework core functionality
    
    Tests the core classes and functionality of the GGG framework including:
    - User management
    - Organization operations
    - Base initialization
    - Token and wallet integration
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment before each test"""
        initialize()

    def test_user_creation(self):
        """Test creating a new user with wallet"""
        user = User.new("test_user", "test-principal")
        assert user.principal == "test-principal"
        assert user.wallet is not None
        assert isinstance(user.wallet, Wallet)

    def test_user_group(self):
        """Test user group management"""
        group = UserGroup.new("test_group")
        user = User.new("group_test_user", "group-test-principal")
        group.add_member(user)
        members = group.members()
        assert len(members) == 1
        assert members[0].id == user.id

    def test_organization_creation(self):
        """Test creating a new organization with token and wallet"""
        org = Organization.new("test_org", "Test Organization")
        assert org.id == "test_org"
        assert org.wallet is not None
        assert isinstance(org.wallet, Wallet)
        assert org.token is not None
        assert isinstance(org.token, Token)

    def test_organization_join(self):
        """Test user joining an organization"""
        org = Organization.new("join_test_org")
        user = User.new("join_test_user", "join-test-principal")
        user.join(org)
        members = org.members()
        assert len(members) == 1
        assert members[0].id == user.id

    def test_organization_proposal(self):
        """Test creating and processing proposals in organization"""
        org = Organization.new("proposal_test_org")
        proposal = org.create_proposal(
            "Test Proposal",
            "Description",
            "print('test')",
            "test_user"
        )
        assert proposal.title == "Test Proposal"
        assert proposal.description == "Description"
        assert proposal.code == "print('test')"
        assert proposal.creator == "test_user"

    def test_wallet_operations(self):
        """Test basic wallet functionality"""
        wallet = Wallet.new()
        assert wallet.balance == 0
        # Note: Further wallet tests would depend on specific token implementation


if __name__ == '__main__':
    pytest.main(['-v', __file__])
