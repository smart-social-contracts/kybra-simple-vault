import os

# import logging
# logging.basicConfig(level=logging.DEBUG)

import asyncio
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import encode, decode, Types

CANISTER_ID = os.environ.get('CANISTER_ID')
print('CANISTER_ID', CANISTER_ID)

iden = Identity()
client = Client()
agent = Agent(iden, client)
# read governance candid from file
governance_did = open(r"src/declarations/canister_main/canister_main.did").read()
# create a governance canister instance
governance = Canister(agent=agent, canister_id=CANISTER_ID, candid=governance_did)
# call canister method with instance

# async def async_test():
#     res = await governance.greet('tester')
#     print('res', res)

# asyncio.run(async_test())

# query the name of token canister `gvbup-jyaaa-aaaah-qcdwa-cai`
name = agent.query_raw(CANISTER_ID, "name", encode([]))
print('name', name)