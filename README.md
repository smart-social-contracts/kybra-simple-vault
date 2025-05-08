# Kybra Simple Vault

A canister written in Python using Kybra with the following features:
- Users can deposit chain-key tokens (currently, only ckBTC is supported). The vault keeps track of the user's "balances", meaning the net number of tokens each user has deposited into the vault and have been withdrawn out from the vault to the user.
- Only the admin can transfer tokens out of the vault.
- Balance and transaction history per user can be queried.
- The canister makes calls to the [official ICRC compliant ledger and indexer canisters](https://github.com/dfinity/ic/releases?q=ledger-suite-icrc&expanded=true).


**WARNING: This is not ready for production use yet and funds stored in the vault canister can be lost. Use at your own risk.**

[![Test on IC](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test_ic.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![Test](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![License](https://img.shields.io/github/license/smart-social-contracts/kybra-simple-vault.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/blob/main/LICENSE)


## Getting Started

### Quickstart


```bash
# Deploy a vault ready to be used being your principal the admin.
$ dfx deploy vault

# Get an overview of the state of the vault.
$ dfx canister call vault status --output json
{
  "data": {
    "Stats": {
      "app_data": {
        "admin_principal": "ah6ac-cc73l-bb2zc-ni7bh-jov4q-roeyj-6k2ob-mkg5j-pequi-vuaa6-2ae",
        "max_iteration_count": "5",
        "max_results": "20",
        "scan_end_tx_id": "2_467_102",
        "scan_oldest_tx_id": "2_467_102",
        "scan_start_tx_id": "2_467_102",
        "sync_status": "Synced",
        "sync_tx_id": "2_467_102"
      },
      "balances": [
        {
          "amount": "906",
          "principal_id": "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe"
        },
        {
          "amount": "-15",
          "principal_id": "ah6ac-cc73l-bb2zc-ni7bh-jov4q-roeyj-6k2ob-mkg5j-pequi-vuaa6-2ae"
        },
        {
          "amount": "891",
          "principal_id": "guja4-2aaaa-aaaam-qdhjq-cai"
        }
      ],
      "canisters": [
        {
          "id": "ckBTC indexer",
          "principal": "n5wcd-faaaa-aaaar-qaaea-cai"
        },
        {
          "id": "ckBTC ledger",
          "principal": "mxzaz-hqaaa-aaaar-qaada-cai"
        }
      ]
    }
  },
  "success": true
}

# Update the transaction history of the vault.
$ dfx canister call vault update_transaction_history --output json
{
  "data": {
    "TransactionSummary": {
      "new_txs_count": "4"
    }
  },
  "success": true
}

# Get the balance for a specific principal.
$ dfx canister call vault get_balance '(principal "...")' --output json
{
  "data": {
    "Balance": {
      "amount": "4_014",
      "principal_id": "ah6ac-cc73l-bb2zc-ni7bh-jov4q-roeyj-6k2ob-mkg5j-pequi-vuaa6-2ae"
    }
  },
  "success": true
}

# Get all the transactions for a specific principal.
$ dfx canister call vault get_transactions '(principal "...")' --output json
{
  "data": {
    "Transactions": [
      {
        "amount": "1_005",
        "id": "5",
        "timestamp": "1_746_721_396_182_936_275"
      },
      ...
      {
        "amount": "1_002",
        "id": "2",
        "timestamp": "1_746_721_392_122_493_649"
      }
    ]
  },
  "success": true
}

# Send tokens to a specific address (only the admin can do this operation).
$ dfx canister call vault transfer '(principal "...", 100)' --output json
{
  "data": {
    "TransactionId": {
      "transaction_id": "6"
    }
  },
  "success": true
}

```


### Installation

```bash
# Clone the repository
git clone https://github.com/smart-social-contracts/kybra-simple-vault.git
cd kybra-simple-vault

# Recommended setup
pyenv install 3.10.7
pyenv local 3.10.7
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Running tests
./run_linters.sh --fix && ./run_test.sh
```

### Syncing

The syncing mechanism is run by an external call to the `update_transaction_history` method. The syncing process is limited by the `max_iteration_count` and `max_results` parameters.
Syncing is guaranteed regardless of how many unprocessed transactions there are, as long as the `update_transaction_history` method is called enough times.

## License

MIT
