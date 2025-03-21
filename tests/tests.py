import os
import sys
import pytest
import json
import time
import requests
from pathlib import Path
from pytest import mark

from test_utils import check
from test_data import RUN_CODE_RESPONSE

# Constants
THIS_DIR = Path(__file__).parent
SCENARIOS_DIR = THIS_DIR / "scenarios"


def ensure_local_server_running():
    """Ensure local server is running if TEST_LOCAL is set"""
    if os.environ.get('TEST_LOCAL'):
        try:
            response = requests.get('http://localhost:8000/greet')
            if response.status_code != 200:
                raise Exception("Local server is not responding correctly")
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Local server is not running. Please start it with:\n"
                "PYTHONPATH=src/canister_main python src/local/main.py"
            )


class TestScenario:
    """Test suite for canister main functionality
    
    This test suite can run against either:
    1. The actual canister (default) using dfx commands
    2. A local HTTP server when TEST_LOCAL environment variable is set
    
    To run tests against local server:
    1. Start the server: PYTHONPATH=src/canister_main python src/local/main.py
    2. Run tests: TEST_LOCAL=1 pytest tests/tests.py
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure environment is properly set up before each test"""
        ensure_local_server_running()

    @pytest.fixture
    def extension_code(self):
        """Load extension code from file"""
        return (SCENARIOS_DIR / "complete/extension.py").read_text()

    def get_json_file(self, name):
        """Load JSON data from file"""
        return json.loads((SCENARIOS_DIR / f"complete/{name}.json").read_text())

    @pytest.fixture
    def dfx_command(self):
        """Base dfx command with canister"""
        return ["dfx", "canister", "call", "canister_main"]

    @mark.order(1)
    def test_run_code(self, dfx_command, extension_code):
        """Test running extension code"""
        command = dfx_command + ["run_code", extension_code]
        assert check(command, RUN_CODE_RESPONSE) == 0, "Code execution failed"

    @mark.order(2)
    def test_get_universe(self, dfx_command):
        """Test the get_universe endpoint returns correct state after running code"""
        command = dfx_command + ["get_universe"]
        assert check(
            command, self.get_json_file('extension')) == 0, "Unexpected universe data"

    @mark.order(3)
    def test_get_organization_list(self, dfx_command):
        """Test getting organization list"""
        command = dfx_command + ["get_organization_list"]
        assert check(command, self.get_json_file('get_organization_list')) == 0, "Failed to get organization list"

    @mark.order(4)
    def test_get_organization_data(self, dfx_command):
        """Test getting organization data"""
        command = dfx_command + ["get_organization_data", "state"]
        assert check(command, self.get_json_file('get_organization_data')) == 0, "Failed to get organization data"

    @mark.order(5)
    def test_get_proposal_data(self, dfx_command):
        """Test getting proposal data"""
        command = dfx_command + ["get_proposal_data", "0"]
        assert check(command, self.get_json_file('get_proposal_data')) == 0, "Failed to get proposal data"

    # @mark.order(4)
    # def test_create_user(self, dfx_command, test_user_data):
    #     """Test creating a new user"""
    #     command = dfx_command + ["create_user"]
    #     assert check(command, test_user_data) == 0, "Failed to create user"

    # @mark.order(5)
    # def test_get_user_data(self, dfx_command, test_user_data):
    #     """Test getting user data"""
    #     command = dfx_command + ["get_user_data", test_user_data["id"]]
    #     assert check(command, test_user_data) == 0, "Failed to get user data"

    # @mark.order(6)
    # def test_get_user_list(self, dfx_command):
    #     """Test getting user list"""
    #     command = dfx_command + ["get_user_list"]
    #     # After creating a user, expect a list with one user
    #     assert check(command, [{"id": "user1", "name": "Test User"}]) == 0, "Failed to get user list"

    # @mark.order(7)
    # def test_get_token_list(self, dfx_command):
    #     """Test getting token list"""
    #     command = dfx_command + ["get_token_list"]
    #     # Initially expect an empty list
    #     assert check(command, []) == 0, "Failed to get token list"

    # @mark.order(8)
    # def test_get_token_data(self, dfx_command, test_token_data):
    #     """Test getting token data"""
    #     command = dfx_command + ["get_token_data", test_token_data["id"]]
    #     # Initially expect None since token doesn't exist
    #     assert check(command, None) == 0, "Failed to get token data"

    # @mark.order(9)
    # def test_user_join_organization(self, dfx_command, test_user_data):
    #     """Test user joining organization"""
    #     command = dfx_command + ["user_join_organization", test_user_data["id"]]
    #     # Expect success response
    #     assert check(command, True) == 0, "Failed to join organization"


if __name__ == '__main__':
    pytest.main(['-v', __file__])
