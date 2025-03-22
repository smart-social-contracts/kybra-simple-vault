source .env

export PRINCIPAL=$(dfx identity get-principal)


dfx canister call $MAINNET_CKBTC_INDEX_CANISTER icrc1_balance_of '(record {owner = principal "'${PRINCIPAL}'"})' --ic --output json
dfx canister call $MAINNET_CKBTC_MINTER_CANISTER get_btc_address "(record {owner = opt principal \"$PRINCIPAL\"; })" --ic --output json


dfx canister call $MAINNET_CKBTC_LEDGER_CANISTER get_transactions '(record { start = 2_321_413 : nat; length = 10 : nat })' --ic --output json


