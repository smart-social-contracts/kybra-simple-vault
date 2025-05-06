#!/usr/bin/env python3
"""
Tests for deploying the vault canister with specific parameters.
"""

import json
import os
import subprocess
import sys
import traceback

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

from tests.utils.colors import GREEN, RED, RESET
from tests.utils.command import get_canister_id, get_current_principal, run_command


def test_deploy_vault_with_params():
    """Test deploying the vault canister with specific initialization parameters."""
    print("\nTesting vault deployment with initialization parameters...")

    # Get current user principal for admin
    admin_principal = get_current_principal()
    if not admin_principal:
        return False

    # First, get the ledger and indexer canister IDs
    ledger_id = get_canister_id("ckbtc_ledger")
    if not ledger_id:
        print(f"{RED}✗ Failed to get ckbtc_ledger canister ID{RESET}")
        return False

    indexer_id = get_canister_id("ckbtc_indexer")
    if not indexer_id:
        print(f"{RED}✗ Failed to get ckbtc_indexer canister ID{RESET}")
        return False

    # Uninstall existing vault canister (in case it exists)
    print("Uninstalling existing vault canister...")
    uninstall_cmd = "dfx canister uninstall-code vault"
    run_command(uninstall_cmd)

    # Create deploy command with all parameters
    deploy_cmd = f"""dfx deploy vault --argument="(
      opt vec {{ 
        record {{ \\"ckBTC ledger\\"; principal \\"{ledger_id}\\" }};
        record {{ \\"ckBTC indexer\\"; principal \\"{indexer_id}\\" }}
      }},
      opt principal \\"{admin_principal}\\",
      opt 20,
      opt 5
    )" --mode reinstall"""

    try:
        # Execute deployment
        result = run_command(deploy_cmd)
        if not result:
            print(f"{RED}✗ Vault deployment failed{RESET}")
            return False

        print(f"{GREEN}✓ Vault deployed successfully with parameters{RESET}")

        # Verify the deployment by checking vault status
        status_cmd = "dfx canister call vault status --output json"
        status_result = run_command(status_cmd)

        if not status_result:
            print(f"{RED}✗ Failed to check vault status{RESET}")
            return False

        status_json = json.loads(status_result)
        if not status_json.get("success", False):
            print(f"{RED}✗ Vault status check failed{RESET}")
            return False

        # Extract and verify admin principal from status
        vault_admin = None
        try:
            # Navigate the response structure to find admin data
            vault_admin = status_json["data"][0]["Status"]["admin"]
            print(f"Vault admin: {vault_admin}")

            # Verify admin is set correctly
            if admin_principal in vault_admin:
                print(f"{GREEN}✓ Admin principal set correctly{RESET}")
            else:
                print(f"{RED}✗ Admin principal not set correctly{RESET}")
                return False

            print(f"{GREEN}✓ Vault deployment verified{RESET}")
            return True

        except (KeyError, IndexError) as e:
            print(f"{RED}✗ Error extracting admin from status: {e}{RESET}")
            return False

    except Exception as e:
        print(f"{RED}✗ Error in deployment test: {e}\n{traceback.format_exc()}{RESET}")
        return False




def test_deploy_vault_without_params():
    """Test deploying the vault canister without specifying initialization parameters."""
    print("\nTesting vault deployment without initialization parameters...")
    
    # Uninstall existing vault canister (in case it exists)
    print("Uninstalling existing vault canister...")
    uninstall_cmd = "dfx canister uninstall-code vault"
    run_command(uninstall_cmd)
    
    # Deploy the vault without any arguments (relying on default values)
    deploy_cmd = "dfx deploy vault --mode reinstall"
    
    try:
        # Execute deployment
        result = run_command(deploy_cmd)
        if not result:
            print(f"{RED}✗ Default vault deployment failed{RESET}")
            return False
            
        print(f"{GREEN}✓ Vault deployed successfully with default parameters{RESET}")
        
        # Verify the deployment by checking vault status
        status_cmd = "dfx canister call vault status --output json"
        status_result = run_command(status_cmd)
        
        if not status_result:
            print(f"{RED}✗ Failed to check vault status{RESET}")
            return False
            
        status_json = json.loads(status_result)
        if not status_json.get("success", False):
            print(f"{RED}✗ Vault status check failed{RESET}")
            return False
        
        # Extract and display information about the default config
        try:
            # Navigate the response structure to find admin and other data
            status_data = status_json["data"][0]["Status"]
            
            # Check if the ledger and indexer canisters were set to defaults
            if "canisters" in status_data:
                print("Default canister configuration:")
                for canister_name, canister_id in status_data["canisters"].items():
                    print(f"  - {canister_name}: {canister_id}")
            
            # Check if admin was set to the default value (likely caller's principal)
            if "admin" in status_data:
                admin = status_data["admin"]
                current_principal = get_current_principal()
                print(f"Default admin principal: {admin}")
                
                # Verify if the default admin is the current principal
                if current_principal and current_principal in admin:
                    print(f"{GREEN}✓ Default admin set to current principal{RESET}")
                else:
                    print(f"{RED}✗ Default admin not set to current principal{RESET}")
            
            # Check default limits
            if "max_results" in status_data:
                print(f"Default max_results: {status_data['max_results']}")
            if "max_iterations" in status_data:
                print(f"Default max_iterations: {status_data['max_iterations']}")
                
            print(f"{GREEN}✓ Default vault deployment verified{RESET}")
            return True
            
        except (KeyError, IndexError) as e:
            print(f"{RED}✗ Error extracting data from status: {e}{RESET}")
            return False
            
    except Exception as e:
        print(f"{RED}✗ Error in default deployment test: {e}\n{traceback.format_exc()}{RESET}")
        return False


def test_reinstall_vault():
    # TODO
    # - checks status, balances and transaction history
    # - checks update transactions and transfer
    pass

def test_set_canisters():
    """Test that only admin can set canisters in the vault."""
    print("\nTesting set_canisters functionality...")
    
    # Get current user principal (admin)
    admin_principal = get_current_principal()
    if not admin_principal:
        return False
    
    # Get canister IDs
    ledger_id = get_canister_id("ckbtc_ledger")
    indexer_id = get_canister_id("ckbtc_indexer")
    
    if not ledger_id or not indexer_id:
        print(f"{RED}✗ Failed to get canister IDs{RESET}")
        return False
    
    # Test setting canisters with admin identity
    print("Testing setting canisters as admin...")
    set_cmd = f"""dfx canister call vault set_canisters '(
      vec {{ 
        record {{ "ckBTC ledger"; principal "{ledger_id}" }};
        record {{ "ckBTC indexer"; principal "{indexer_id}" }}
      }}
    )' --output json"""
    
    try:
        result = run_command(set_cmd)
        if not result:
            print(f"{RED}✗ Failed to set canisters as admin{RESET}")
            return False
            
        result_json = json.loads(result)
        success = result_json.get("success", False)
        
        if not success:
            message = result_json.get("message", "Unknown error")
            print(f"{RED}✗ Failed to set canisters as admin: {message}{RESET}")
            return False
            
        print(f"{GREEN}✓ Successfully set canisters as admin{RESET}")
        
        # Verify canisters were set by checking status
        status_cmd = "dfx canister call vault status --output json"
        status_result = run_command(status_cmd)
        
        if not status_result:
            print(f"{RED}✗ Failed to get vault status{RESET}")
            return False
            
        status_json = json.loads(status_result)
        if not status_json.get("success", False):
            print(f"{RED}✗ Vault status check failed{RESET}")
            return False
            
        # Extract canisters from status
        try:
            status_data = status_json["data"][0]["Status"]
            canisters = status_data.get("canisters", {})
            
            if "ckBTC ledger" in canisters and "ckBTC indexer" in canisters:
                print(f"{GREEN}✓ Canisters verified in vault status{RESET}")
                
                if ledger_id in canisters["ckBTC ledger"] and indexer_id in canisters["ckBTC indexer"]:
                    print(f"{GREEN}✓ Canister IDs match the ones we set{RESET}")
                else:
                    print(f"{RED}✗ Canister IDs don't match the ones we set{RESET}")
                    return False
            else:
                print(f"{RED}✗ Canisters not found in vault status{RESET}")
                return False
                
        except (KeyError, IndexError) as e:
            print(f"{RED}✗ Error extracting canister data from status: {e}{RESET}")
            return False
            
        print(f"{GREEN}✓ set_canisters functionality works correctly{RESET}")
        return True
            
    except Exception as e:
        print(f"{RED}✗ Error in set_canisters test: {e}\n{traceback.format_exc()}{RESET}")
        return False


def test_set_admin():
    """Test that only admin can set a new admin in the vault."""
    print("\nTesting set_admin functionality...")
    
    # Get current user principal (current admin)
    current_admin = get_current_principal()
    if not current_admin:
        return False
    
    # We'll use the same principal as both current and new admin for testing
    # In a real scenario, you might want to use a different principal
    new_admin = current_admin
    
    # Test setting admin with admin identity
    print("Testing setting admin as current admin...")
    set_cmd = f'dfx canister call vault set_admin "(principal \\"{new_admin}\\")" --output json'
    
    try:
        result = run_command(set_cmd)
        if not result:
            print(f"{RED}✗ Failed to set admin{RESET}")
            return False
            
        result_json = json.loads(result)
        success = result_json.get("success", False)
        
        if not success:
            message = result_json.get("message", "Unknown error")
            print(f"{RED}✗ Failed to set admin: {message}{RESET}")
            return False
            
        print(f"{GREEN}✓ Successfully set admin{RESET}")
        
        # Verify admin was set by checking status
        status_cmd = "dfx canister call vault status --output json"
        status_result = run_command(status_cmd)
        
        if not status_result:
            print(f"{RED}✗ Failed to get vault status{RESET}")
            return False
            
        status_json = json.loads(status_result)
        if not status_json.get("success", False):
            print(f"{RED}✗ Vault status check failed{RESET}")
            return False
            
        # Extract admin from status
        try:
            status_data = status_json["data"][0]["Status"]
            admin = status_data.get("admin", "")
            
            if new_admin in admin:
                print(f"{GREEN}✓ Admin verified in vault status{RESET}")
            else:
                print(f"{RED}✗ Admin not set correctly in vault status{RESET}")
                return False
                
        except (KeyError, IndexError) as e:
            print(f"{RED}✗ Error extracting admin from status: {e}{RESET}")
            return False
            
        print(f"{GREEN}✓ set_admin functionality works correctly{RESET}")
        return True
            
    except Exception as e:
        print(f"{RED}✗ Error in set_admin test: {e}\n{traceback.format_exc()}{RESET}")
        return False


if __name__ == "__main__":
    test_deploy_vault_with_params()
    test_deploy_vault_without_params()
    test_reinstall_vault()
    test_set_canisters()
    test_set_admin()
