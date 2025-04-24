# Kybra Simple Vault

A canister written in Python using Kybra that manages ICRC-1 token transactions (e.g., ckBTC) on the Internet Computer.

**WARNING: This is not ready for production use yet and funds stored in the vault canister can be lost. Use at your own risk.**

[![Test on IC](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test_ic.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![Test](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![License](https://img.shields.io/github/license/smart-social-contracts/kybra-simple-vault.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/blob/main/LICENSE)

## Features

- Receive tokens from any principal and track balances
- Admin can withdraw tokens to specific addresses
- Query balances, transaction history and statistics
- Automatic background synchronization with the ledger via heartbeat

## Getting Started

### Prerequisites

- Python 3.10
- dfx

### Quick Start

```bash
# Clone the repository
git clone https://github.com/smart-social-contracts/kybra-simple-vault.git
cd kybra-simple-vault

# Deploy the vault canister with default arguments on the Internet Computer
dfx deploy vault --network ic --argument '(null, null, null, 0)'
```

This will deploy the vault canister with default arguments, which will use the mainnet ckBTC ledger canister and your identity as the admin of the vault.


### Vault Canister Initialization

```bash
dfx deploy vault --argument='(opt "<id>", opt principal "<princ>", opt principal "<admin>", <seconds>)'
```

The `vault` canister supports optional init arguments for flexible deployment:
- `ledger_canister_id` (opt text)
- `ledger_canister_principal` (opt principal)
- `admin_principal` (opt principal)
- `heartbeat_interval_seconds` (nat, default 0)

If not provided, ledger args default to mainnet values; admin defaults to the deployer. If you set one ledger arg, set both.


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

Admin functions:

```bash
# Reset the vault
dfx canister call vault reset

# Set admin
dfx canister call vault set_admin "<admin_principal>"

# Set heartbeat interval
dfx canister call vault set_heartbeat_interval_seconds <seconds>

# Set ledger canister
dfx canister call vault set_ledger_canister "<id>" "<principal>"

# Transfer tokens out of the vault (amount in smallest unit, e.g., 100000000 for 1 ckBTC)
dfx canister call vault do_transfer "<to>" <amount>
```

## License

MIT
