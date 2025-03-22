# kybra-simple-vault

This project allows to:


for icp users
    give them a unique ckBTC/ckETH/ckUSDC address for all of them
    scan for deposits into that address and internally allocate their ck to the realm treasury
    Future improvement: use subaccounts

(in the future:
for non-icp users
    use ck minter to give them a native address (BTC, ETH or USDC)
    take the minted ck to the realm treasury
)

# TODO steps

for non-icp users
    recall the ckminter dfx commands and translate them into kybra



for icp users
    come up with the dfx commands and write a kybra code that scans for ck transactions to a certain principal
    dfx command to transfer ck tokens from the canister out of the user


```
$ dfx canister --network ic call mxzaz-hqaaa-aaaar-qaada-cai icrc1_balance_of '(
  record { 
    owner = principal "64fpo-jgpms-fpewi-hrskb-f3n6u-3z5fy-bv25f-zxjzg-q5m55-xmfpq-hqe"; 
    subaccount = null 
  }
)'
(7_169 : nat)
```

`dfx canister --ic call qaa6y-5yaaa-aaaaa-aaafa-cai get_transactions '(record { start = 0; length = 10 })'`
Tells you where to find the transactions in the archiving ledger canister

`dfx canister --network ic call nbsys-saaaa-aaaar-qaaga-cai get_blocks '(record { start = 10000; length = 10 })'`
Returns the actual transaction data