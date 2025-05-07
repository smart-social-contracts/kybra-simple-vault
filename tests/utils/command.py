#!/usr/bin/env python3
"""
Utility functions for running commands and interacting with canisters.
"""

import json
import os
import subprocess
import sys

from tests.utils.colors import print_error, print_ok

# Add the parent directory to the Python path to make imports work
sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


def run_command(command):
    """Run a shell command and return its output."""
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print_error(f"Error executing command: {command}")
        print_error(f"Error: {process.stderr}")
        return None
    return process.stdout.strip()


def run_command_expects_response_obj(command):
    """Run a shell command and return its output as a JSON object."""
    result = run_command(command)
    if not result:
        print_error(f"✗ Failed to run command `{command}`")
        return False

    result_json = json.loads(result)
    success = result_json.get("success", False)

    if not success:
        message = result_json.get("message", "Unknown error")
        print_error(f"✗ Failed to run command `{command}`: {message}")
        return False

    return result_json


def get_canister_id(canister_name):
    """Get the canister ID for the given canister name."""
    result = run_command(f"dfx canister id {canister_name}")
    if not result:
        raise Exception(f"Failed to get ID of canister {canister_name}")
    return result


def get_current_principal():
    """Get the principal ID of the current identity."""
    principal = run_command("dfx identity get-principal")
    if not principal:
        raise Exception("Failed to get principal")
    return principal


def deploy_ckbtc_ledger(
    initial_balance=1_000_000_000,
    transfer_fee=10,
    identities=None,
    identity_balances=None,
):
    """
    Deploy the ckBTC ledger canister with specified parameters.

    Args:
        initial_balance: Initial token balance for the current principal
        transfer_fee: Fee for token transfers
        identities: Optional dict mapping identity names to principals (from create_test_identities)
        identity_balances: Optional dict mapping identity names to their initial balances
                          If not provided, identities will have zero balance

    Returns:
        str: Canister ID of the deployed ledger, or None if deployment failed
    """
    print("Deploying ckbtc_ledger canister...")

    # Get current principal for controller and initial balance
    current_principal = get_current_principal()
    if not current_principal:
        return None

    # Fixed minting principal for test environment
    minting_principal = "aaaaa-aa"

    # Build the initial balances section
    balance_entries = []

    # Add current principal balance first
    balance_entries.append(
        f"""record {{ 
            record {{ 
              owner = principal \\"{current_principal}\\"; 
              subaccount = null 
            }}; 
            {initial_balance} 
          }}"""
    )

    # Add balances for identities if provided
    if identities and identity_balances:
        for name, principal_id in identities.items():
            if name in identity_balances:
                balance = identity_balances[name]
                balance_entries.append(
                    f"""record {{ 
            record {{ 
              owner = principal \\"{principal_id}\\"; 
              subaccount = null 
            }}; 
            {balance} 
          }}"""
                )

    # Join the entries with semicolons (Candid syntax) to avoid trailing commas
    initial_balances_vec = "; ".join(balance_entries)

    # Construct the deploy command with all parameters
    deploy_cmd = f"""dfx deploy --no-wallet ckbtc_ledger --argument="(variant {{ 
      Init = record {{ 
        minting_account = record {{ 
          owner = principal \\"{minting_principal}\\"; 
          subaccount = null 
        }}; 
        transfer_fee = {transfer_fee}; 
        token_symbol = \\"ckBTC\\"; 
        token_name = \\"ckBTC Test\\"; 
        decimals = opt 8; 
        metadata = vec {{}}; 
        initial_balances = vec {{ 
          {initial_balances_vec}
        }}; 
        feature_flags = opt record {{ 
          icrc2 = true 
        }}; 
        archive_options = record {{ 
          num_blocks_to_archive = 1000; 
          trigger_threshold = 2000; 
          controller_id = principal \\"{current_principal}\\" 
        }} 
      }} 
    }})" """

    # Execute the deploy command
    run_command(deploy_cmd)

    # Get the ledger canister ID
    ledger_id = get_canister_id("ckbtc_ledger")
    if ledger_id:
        print_ok(f"✓ ckbtc_ledger canister deployed with ID: {ledger_id}")

    return ledger_id


def deploy_ckbtc_indexer(ledger_id=None, interval_seconds=1):
    """
    Deploy the ckBTC indexer canister with specified parameters.

    Args:
        ledger_id: Principal ID of the ckBTC ledger canister
        interval_seconds: Interval in seconds for retrieving blocks from ledger

    Returns:
        str: Canister ID of the deployed indexer, or None if deployment failed
    """
    print("Deploying ckbtc_indexer canister...")

    # If ledger_id not provided, try to get it
    if not ledger_id:
        ledger_id = get_canister_id("ckbtc_ledger")
        if not ledger_id:
            print_error("Cannot deploy indexer: ckbtc_ledger canister ID not found")
            return None

    # Construct the deploy command
    deploy_cmd = f"""dfx deploy --no-wallet ckbtc_indexer --argument="(opt variant {{ 
      Init = record {{ 
        ledger_id = principal \\"{ledger_id}\\"; 
        retrieve_blocks_from_ledger_interval_seconds = opt {interval_seconds} 
      }} 
    }})" """

    # Execute the deploy command
    run_command(deploy_cmd)

    # Get the indexer canister ID
    indexer_id = get_canister_id("ckbtc_indexer")
    if indexer_id:
        print_ok(f"ckbtc_indexer canister deployed with ID: {indexer_id}")

    return indexer_id


def update_transaction_history_until_no_more_transactions():
    loop_count = 0
    while loop_count < 20:
        loop_count += 1
        response = run_command(
            "dfx canister call vault update_transaction_history --output json"
        )
        response_json = json.loads(response)
        success = response_json.get("success", False)
        if not success:
            print_error("Failed to update transaction history")
            return False

        new_count = int(
            response_json.get("data")[0].get("TransactionSummary").get("new_txs_count")
        )
        print(f"New count: {new_count}")
        if new_count == 0:
            return True

    raise Exception(
        "Failed to update transaction history completely after max iteration_count"
    )


def generate_transaction_commands(transactions):
    """
    Generate dfx commands for a list of transaction data.

    Args:
        transactions: List of dictionaries containing transaction data.
                     Each transaction should have at minimum:
                     - 'type': 'to_vault' or 'from_vault'
                     - 'principal': Principal ID for the transaction
                     - 'amount': Amount to transfer

                     Optional fields:
                     - 'memo': Memo for the transaction (only for to_vault)
                     - 'subaccount': Subaccount (only for to_vault)
                     - 'fee': Fee for the transaction (only for to_vault)

    Returns:
        List of strings, each containing a dfx command ready to be executed.
    """
    commands = []

    for tx in transactions:
        # Validate required fields
        if "type" not in tx or "principal" not in tx or "amount" not in tx:
            print_error(f"Transaction missing required fields: {tx}")
            continue

        if tx["type"] == "from_vault":
            # Transfer from vault to a principal
            cmd = f"dfx canister call vault transfer '(principal \"{tx['principal']}\", {tx['amount']})' --output json"
            commands.append(cmd)

        elif tx["type"] == "to_vault":
            # Transfer from a principal to the vault
            # Get the vault canister ID
            vault_id = get_canister_id("vault")
            if not vault_id:
                print_error("Failed to get vault canister ID")
                continue

            # Build the subaccount part
            subaccount_part = f"subaccount = {tx.get('subaccount', 'null')}"

            # Build the fee part
            fee_part = f"fee = {tx.get('fee', 'null')}"

            # Build the memo part
            memo_part = f"memo = {tx.get('memo', 'null')}"

            # Build the from_subaccount part
            from_subaccount_part = (
                f"from_subaccount = {tx.get('from_subaccount', 'null')}"
            )

            # Build the created_at_time part
            created_at_time_part = (
                f"created_at_time = {tx.get('created_at_time', 'null')}"
            )

            # Construct the full command
            cmd = f"dfx canister call ckbtc_ledger icrc1_transfer '(record {{ to = record {{ owner = principal \"{vault_id}\"; {subaccount_part} }}; amount = {tx['amount']}; {fee_part}; {memo_part}; {from_subaccount_part}; {created_at_time_part} }})' --output json"
            commands.append(cmd)

        elif tx["type"] == "update_history":
            # Command to update transaction history
            cmd = "dfx canister call vault update_transaction_history --output json"
            commands.append(cmd)

        elif tx["type"] == "get_transactions":
            # Command to get transactions for a principal
            cmd = "dfx canister call vault get_transactions '(\"{tx['principal']}\")' --output json"
            commands.append(cmd)

        elif tx["type"] == "get_balance":
            # Command to get balance for a principal
            cmd = f"dfx canister call vault get_balance '(\"{tx['principal']}\")' --output json"
            commands.append(cmd)

        else:
            print_error(f"Unknown transaction type: {tx['type']}")

    return commands


def execute_transactions(
    transaction_pairs, identities=None, start_amount=101, initial_balances=None
):
    """
    Execute transactions with balance tracking.

    Args:
        transaction_pairs: Pairs of [from, to] with 'vault', identity names, or 'principal'
        identities: Dict of identity names to principals (from create_test_identities)
        start_amount: Starting amount (increments by 1 for each transaction)
        initial_balances: Optional starting balances for accounts

    Returns:
        (success, final_balances)
    """
    amount = start_amount
    success = True

    # Set up principals map
    principals = {"principal": get_current_principal()}
    if identities:
        principals.update(identities)

    # Initialize balances
    # For regular token balances (outside vault)
    token_balances = {}
    if initial_balances:
        token_balances = initial_balances.copy()

    # For vault balances (net deposits)
    vault_balances = {"vault": 0}
    for user in list(principals.keys()):
        if user not in token_balances:
            token_balances[user] = 0
        vault_balances[user] = 0  # Initialize vault balance to 0

    # Process each transaction
    for sender, receiver in transaction_pairs:
        if sender == "update_history":
            run_command(
                "dfx canister call vault update_transaction_history --output json"
            )
            continue

        if sender == "check_balance":
            # receiver should be the name of the identity to check
            if receiver in principals:
                principal_id = principals[receiver]
                expected_amount = vault_balances.get(receiver, 0)

                from tests.test_cases.balance_tests import check_balance

                actual_balance, balance_success = check_balance(
                    principal_id, expected_amount
                )

                if not balance_success:
                    print_error(f"Balance verification failed for {receiver}")
                    success = False
            elif receiver == "vault":
                vault_id = get_canister_id("vault")
                expected_amount = vault_balances.get("vault", 0)

                from tests.test_cases.balance_tests import check_balance

                actual_balance, balance_success = check_balance(
                    vault_id, expected_amount
                )

                if not balance_success:
                    print_error("Balance verification failed for vault")
                    success = False
            else:
                print_error(f"Unknown identity for balance check: {receiver}")
                success = False
            continue

        # Get sender and receiver principals/identities
        sender_principal = (
            principals.get(sender, sender) if sender != "vault" else "vault"
        )
        receiver_principal = (
            principals.get(receiver, receiver) if receiver != "vault" else "vault"
        )

        print(f"Transaction: {sender} -> {receiver}, amount: {amount}")

        # Track token balances (outside the vault)
        if sender != "vault" and sender in token_balances:
            token_balances[sender] -= amount
        if receiver != "vault" and receiver in token_balances:
            token_balances[receiver] += amount

        # Track vault balances (net deposits)
        if sender == "vault" and receiver in vault_balances:
            # Vault is sending to user (withdrawal)
            vault_balances[receiver] -= amount
        elif receiver == "vault" and sender in vault_balances:
            # User is sending to vault (deposit)
            vault_balances[sender] += amount

        # Execute transfer
        sender_id = "vault" if sender == "vault" else principals.get(sender, sender)
        receiver_id = (
            "vault" if receiver == "vault" else principals.get(receiver, receiver)
        )

        if sender == "vault":
            cmd = f"""dfx canister call vault transfer '(
                principal "{receiver_id}",
                {amount}
            )' --output json"""

        elif receiver == "vault":
            # User sending to vault - need to transfer via ledger
            identity_arg = f"--identity {sender}" if sender in identities else ""

            # Get vault canister ID
            vault_id = get_canister_id("vault")
            if not vault_id:
                print_error("Failed to get vault canister ID")
                success = False
                continue

            # Transfer tokens to the vault via ledger
            transfer_cmd = f"""dfx {identity_arg} canister call ckbtc_ledger icrc1_transfer '(
                record {{ 
                    to = record {{ 
                        owner = principal "{vault_id}"; 
                        subaccount = null 
                    }}; 
                    amount = {amount}; 
                    fee = null; 
                    memo = null; 
                    from_subaccount = null; 
                    created_at_time = null 
                }}
            )' --output json"""

            print(f"Transferring {amount} tokens from {sender} to vault via ledger...")
            transfer_result = run_command(transfer_cmd)
            if not transfer_result:
                print_error(f"Failed to transfer tokens from {sender} to vault")
                success = False
                continue

            transfer_json = json.loads(transfer_result)
            if "Err" in transfer_json:
                print_error(f"Transfer error: {transfer_json['Err']}")
                success = False
                continue

            print(f"Transfer successful: {transfer_json}")

            # Now tell the vault to update transaction history
            update_cmd = (
                "dfx canister call vault update_transaction_history --output json"
            )
            update_result = run_command(update_cmd)
            if not update_result:
                print_error("Failed to update transaction history")

            cmd = transfer_cmd  # For logging

        else:
            # Get current identity's principal
            current_principal = get_current_principal()

            # If sender is not the current principal, we need to switch identities
            identity_arg = f"--identity {sender}" if sender in identities else ""

            cmd = f"""dfx {identity_arg} canister call vault send '(
                principal "{receiver_id}",
                {amount}
            )' --output json"""

            # Run the transaction command
            tx_result = run_command(cmd)
            if not tx_result or not json.loads(tx_result).get("success", False):
                print_error(f"Transaction failed: {sender} -> {receiver}")
                success = False

        amount += 1

    return success, vault_balances


def create_test_identities(identity_names):
    """
    Create test dfx identities.

    Args:
        identity_names: List of identity names to create (e.g. ['alice', 'bob'])

    Returns:
        Dictionary mapping identity names to their principal IDs
    """
    identities = {}
    current_identity = run_command("dfx identity whoami")

    try:
        for name in identity_names:
            # Create identity if needed
            existing = run_command("dfx identity list")
            if name not in existing.split():
                run_command(f"dfx identity new --disable-encryption {name}")

            # Get principal ID
            run_command(f"dfx identity use {name}")
            principal = get_current_principal()

            if principal:
                identities[name] = principal
                print(f"{name}: {principal}")
    finally:
        run_command(f"dfx identity use {current_identity}")

    return identities
