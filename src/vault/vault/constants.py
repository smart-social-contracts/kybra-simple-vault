# Canister Configuration and System Limits

# Dictionary of canister principal IDs implementing Chain-Key tokens in the IC
# Each token has a corresponding ledger canister for token operations
# and an indexer canister for transaction history and queries
CANISTER_PRINCIPALS = {
    "ckBTC": {
        "ledger": "mxzaz-hqaaa-aaaar-qaada-cai",
        "indexer": "n5wcd-faaaa-aaaar-qaaea-cai",
    }
}

# Maximum number of results to return in paginated responses
# Used to limit the size of transaction history and other list responses
MAX_RESULTS = 20

# Maximum number of iterations for operations that process data in batches
# Prevents infinite loops and excessive resource consumption
MAX_ITERATION_COUNT = 5
