# Kybra Simple Vault

A canister written in Python using Kybra that manages cryptocurrency transactions on the Internet Computer.

[![Test](https://github.com/smart-social-contracts/kybra-simple-vault/actions/workflows/test.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/actions)
[![PyPI version](https://badge.fury.io/py/kybra-simple-vault.svg)](https://badge.fury.io/py/kybra-simple-vault)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![License](https://img.shields.io/github/license/smart-social-contracts/kybra-simple-vault.svg)](https://github.com/smart-social-contracts/kybra-simple-vault/blob/main/LICENSE)

## Features

- Receive ckBTC/ckETH/ckUSDC from any principal and track balances
- Withdraw ckBTC/ckETH/ckUSDC to specific addresses
- Administrative controls for managing withdrawals
- Balance queries for principals

## Getting Started

To use this canister, you'll need access to the Internet Computer and the DFX toolkit.

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
# Check balance
dfx canister call vault get_balance '(principal "$(dfx identity get-principal)")'

# Check logs
dfx canister logs vault
```

## License

MIT
