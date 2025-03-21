
# test(
#     "Basic cURL test",
#     ["curl", "--silent", "http://%s.localhost:4943" % canister_id],
#     'Not found',
# )


# test(
#     "HTTP entrypoint - universe",
#     ["curl", "--silent", "http://%s.localhost:4943/api/v1/get_universe" % canister_id],
#     {
#         'extensions': [
#             {
#                 'creator': IGNORE_TAG,
#                 'id': 'DEFAULT_EXTENSION_CODE_ORGANIZATION',
#                 'owner': IGNORE_TAG,
#                 'source_code': "<IGNORE>",
#                 'timestamp_created': IGNORE_TAG,
#                 'timestamp_updated': IGNORE_TAG,
#                 'type': 'ExtensionCode',
#                 'updater': IGNORE_TAG
#             },
#             {
#                 'creator': IGNORE_TAG,
#                 'id': 'DEFAULT_EXTENSION_CODE_TOKEN',
#                 'owner': IGNORE_TAG,
#                 'source_code': "<IGNORE>",
#                 'timestamp_created': IGNORE_TAG,
#                 'timestamp_updated': IGNORE_TAG,
#                 'tokens': [
#                     'Token@BTC'
#                 ],
#                 'type': 'ExtensionCode',
#                 'updater': IGNORE_TAG
#             }
#         ],
#         'organizations': [

#         ],
#         'tokens': [
#             {
#                 'balances': {

#                 },
#                 'creator': IGNORE_TAG,
#                 'extension_code': [
#                     'ExtensionCode@DEFAULT_EXTENSION_CODE_TOKEN'
#                 ],
#                 'id': 'BTC',
#                 'metadata': {

#                 },
#                 'name': 'Bitcoin',
#                 'owner': IGNORE_TAG,
#                 'timestamp_created': IGNORE_TAG,
#                 'timestamp_updated': IGNORE_TAG,
#                 'type': 'Token',
#                 'updater': IGNORE_TAG
#             }
#         ],
#         'user_groups': [

#         ],
#         'users': [
#             {
#                 'creator': IGNORE_TAG,
#                 'id': 'DEFAULT',
#                 'owner': IGNORE_TAG,
#                 'principal': 'aaa-0',
#                 'timestamp_created': IGNORE_TAG,
#                 'timestamp_updated': IGNORE_TAG,
#                 'type': 'User',
#                 'updater': IGNORE_TAG,
#                 'wallet': [
#                     'Wallet@0'
#                 ]
#             }
#         ]
#     },
# )



# # Test token list endpoint
# test(
#     "HTTP entrypoint - token list",
#     ["curl", "--silent", f"http://{canister_id}.localhost:4943/api/v1/tokens"],
#     [
#         {
#             "balances": {},
#             "creator": IGNORE_TAG,
#             "id": "BTC",
#             "metadata": {},
#             "name": "Bitcoin",
#             "owner": IGNORE_TAG,
#             "timestamp_created": IGNORE_TAG,
#             "timestamp_updated": IGNORE_TAG,
#             "type": "Token",
#             "updater": IGNORE_TAG
#         }
#     ]
# )

# # Test token data endpoint - existing token
# test(
#     "HTTP entrypoint - token data (existing)",
#     ["curl", "--silent", f"http://{canister_id}.localhost:4943/api/v1/tokens/BTC"],
#     {
#         "balances": {},
#         "creator": IGNORE_TAG,
#         "id": "BTC",
#         "metadata": {},
#         "name": "Bitcoin",
#         "owner": IGNORE_TAG,
#         "timestamp_created": IGNORE_TAG,
#         "timestamp_updated": IGNORE_TAG,
#         "type": "Token",
#         "updater": IGNORE_TAG
#     }
# )

# # Test token data endpoint - non-existent token
# test(
#     "HTTP entrypoint - token data (non-existent)",
#     ["curl", "--silent", f"http://{canister_id}.localhost:4943/api/v1/tokens/NONEXISTENT"],
#     {"error": "Token not found"}
# )


# test(
#     "Basic test - extension commit",
#     ["dfx", "canister", "call", "canister_main", "extension_commit", test_py],
#     "()",
# )

# test(
#     "Basic test - extension run",
#     ["dfx", "canister", "call", "canister_main", "extension_run"],
#     {
#         "atributes": {"name": "State A"},
#         "id": "State A",
#         "relations": {"citizens": ["citizen@Alice", "citizen@Bob"]},
#         "type": "state",
#     },
# )


# expected = {
#     "citizens": [
#         {
#             "atributes": {"name": "Alice"},
#             "id": "Alice",
#             "relations": {"states": ["state@State A"]},
#             "type": "citizen",
#         },
#         {
#             "atributes": {"name": "Bob"},
#             "id": "Bob",
#             "relations": {"states": ["state@State A"]},
#             "type": "citizen",
#         },
#     ],
#     "states": [
#         {
#             "atributes": {"name": "State A"},
#             "id": "State A",
#             "relations": {"citizens": ["citizen@Alice", "citizen@Bob"]},
#             "type": "state",
#         }
#     ],
# }
