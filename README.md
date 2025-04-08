# Kybra Simple Vault

A canister written in Python using Kybra that manages cryptocurrency transactions on the Internet Computer.

**WARNING: This is not ready for production use yet and funds stored in the vault canister can be lost. Use at your own risk.**

[![Test on IC](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test_ic.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![Test](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![License](https://img.shields.io/github/license/smart-social-contracts/kybra-simple-vault.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/blob/main/LICENSE)

## Features

- Receive ckBTC from any principal and track balances
- Admin can withdraw ckBTC to specific addresses
- Query balances, transaction history and statistics

## Getting Started

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
