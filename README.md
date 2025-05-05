# Kybra Simple Vault

A canister written in Python using Kybra with which:
- Users can deposit ckBTC
- The admin can withdraw ckBTC to specific addresses
- Balance and transaction history can be queried


**WARNING: This is not ready for production use yet and funds stored in the vault canister can be lost. Use at your own risk.**

[![Test on IC](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test_ic.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![Test](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![License](https://img.shields.io/github/license/smart-social-contracts/kybra-simple-vault.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/blob/main/LICENSE)


## Getting Started

### Quickstart


```bash
# Deploy a vault ready to be used being your principal the admin.
$ dfx deploy

# Get an overview of the state of the vault.
$ dfx canister call vault get_stats 

# Update the transaction history of the vault.
$ dfx canister call vault update_transaction_history

# Get the balance for a specific principal.
$ dfx canister call vault get_balance 

# Get all the transactions for a specific principal.
$ dfx canister call vault get_transactions 

# Send tokens to a specific address
$ dfx canister call vault transfer 


```


### Prerequisites

- Python 3.10
- dfx

### Installation

```bash
# Clone the repository
git clone https://github.com/smart-social-contracts/kybra-simple-vault.git
cd kybra-simple-vault

# Deploy to local replica
dfx start --clean --background
dfx deploy
```

### Usage Examples

```bash
# Check transactions (catches up with the ledger and updates balances according to the transactions processed since the last check)
dfx canister call vault check_transactions

# Check the total balance of the vault
dfx canister call vault get_balance

# Check the statistics
dfx canister call vault get_stats

# Check logs
dfx canister logs vault
```

## License

MIT
