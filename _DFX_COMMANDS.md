source .env

export PRINCIPAL=$(dfx identity get-principal)


dfx canister call $MAINNET_CKBTC_LEDGER_CANISTER icrc1_balance_of '(record {owner = principal "'${PRINCIPAL}'"})' --ic --output json
dfx canister call $MAINNET_CKBTC_LEDGER_CANISTER icrc1_balance_of '(record {owner = principal "guja4-2aaaa-aaaam-qdhjq-cai"})' --ic --output json

dfx canister call $MAINNET_CKBTC_MINTER_CANISTER get_btc_address "(record {owner = opt principal \"$PRINCIPAL\"; })" --ic --output json


dfx canister call $MAINNET_CKBTC_LEDGER_CANISTER get_transactions '(record { start = 2_321_413 : nat; length = 10 : nat })' --ic --output json

dfx deploy ckbtc_ledger --argument '(
  variant {
    Init = record {
      minting_account = record {
        owner = principal "$(dfx identity get-principal)";
        subaccount = null
      };
      transfer_fee = 10;
      token_symbol = "ckBTC";
      token_name = "ckBTC Test";
      decimals = opt 8;
      metadata = vec {};
      initial_balances = vec {
        record {
          record {
            owner = principal "$(dfx identity get-principal)";
            subaccount = null
          };
          1_000_000_000
        },
        record {
          record {
            owner = principal "bd3sg-teaaa-aaaaa-qaaba-cai";
            subaccount = null
          };
          1_000_000_000
        }
      };
      feature_flags = opt record {
        icrc2 = true
      };
      archive_options = record {
        num_blocks_to_archive = 1000;
        trigger_threshold = 2000;
        controller_id = principal "$(dfx identity get-principal)"
      }
    }
  }
)'


dfx canister call ckbtc_ledger icrc1_balance_of "(record {owner = principal \"$(dfx identity get-principal)\"})" --output json

dfx canister call ckbtc_ledger icrc1_balance_of "(record {owner = principal \"bd3sg-teaaa-aaaaa-qaaba-cai\"})" --output json


dfx canister call ckbtc_ledger icrc1_transfer '(
  record {
    to = record {
      owner = principal "bd3sg-teaaa-aaaaa-qaaba-cai";
      subaccount = null;
    };
    fee = null;
    memo = null;
    from_subaccount = null;
    created_at_time = null;
    amount = 1_000 : nat;
  }
)'


dfx canister call vault do_transfer "(principal \"$(dfx identity get-principal)\", 1_000 : nat)"