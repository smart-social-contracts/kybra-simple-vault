# kybra-simple-vault

TODO:
  implement admin
  test on IC docker
  
  github actions including linting
  implement rest of ck currencies
  unify readme (S) / folder structure among projects / cleanup codes simplify
  pipy and releases
    clean, tag Internet Computer Protocol
  
  

A canister written in Python using Kybra that allows to:
- receive ckBTC/ckETH/ckUSDC from any principal and keep track of the balance for each principal
- withdraw ckBTC/ckETH/ckUSDC to a specific address
- set admins (who can withdraw)
- get the balance of a principal
- get the list of admins


methods to:
	get balances
	withdrawt to a specific address
	see status
	
make the heartbeat:
	check if any transfer from anywhere to the canister
	if so, increase the balance (create a key if not yet)
  do the test in non-ic first
	

# dfx commands
dfx ledger balance --ic
dfx cycles top-up vault 1T --network ic
dfx canister --network ic call aaaaa-aa stored_chunks '(record { canister_id = principal "guja4-2aaaa-aaaam-qdhjq-cai" })'
dfx canister --network ic call aaaaa-aa clear_chunk_store '(record {
  canister_id = principal "guja4-2aaaa-aaaam-qdhjq-cai"
})'
dfx canister logs vault --ic


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