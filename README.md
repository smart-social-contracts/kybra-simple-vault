# Kybra Simple Vault

A canister written in Python using Kybra that manages cryptocurrency transactions on the Internet Computer.

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
