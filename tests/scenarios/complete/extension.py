# Time utilities
from stats.snapshot import take_snapshot
from core.system_time import get_system_time, timestamp_to_date, DAY, set_system_time

# Create the main state organization
state = ggg.Organization.new('state')
government = ggg.Organization.new('Government')
tax_department = ggg.Organization.new('Tax Department')

# Link the organizations
state.add_member(government)
government.add_member(tax_department)

# Create users and assign identities
alice = ggg.User.new('alice_identity')
bob = ggg.User.new('bob_identity')

# Join users to the state
state.add_member(alice)
state.add_member(bob)

# Mint BTC tokens to the state wallet and transfer to users
ck_btc = ggg.Token['ckBTC']
# ck_btc.mint(state.wallet.get_address(ck_btc), 10000)
# ck_btc.transfer(state.wallet.get_address(ck_btc), alice.wallet.get_address(ck_btc), 100)
# ck_btc.transfer(state.wallet.get_address(ck_btc), bob.wallet.get_address(ck_btc), 100)



# # Create a new proposal with code
# proposal_code = """
# print('Hello World!!!')
# """.strip()
# now = get_system_time()
# proposal = ggg.Proposal.new(
#     "Proposal to increase budget", proposal_code, now)

# # Submit the proposal to the state and have Bob vote on it
# proposal.submit(state)
# proposal.vote(bob.wallet.get_address(state.token), ggg.Proposal.VOTING_YAY)

# # Advance time to ensure the proposal deadline has passed
# set_system_time(now + DAY)

# # Check proposals and update state if necessary
# state.check_proposals()

# # Create land entity with predefined GeoJSON
# land = ggg.Land.new({
#     "type": "FeatureCollection",
#     "features": [
#         {
#             "type": "Feature",
#             "id": "CHE",
#             "properties": {
#                 "name": "Switzerland"
#             },
#             "geometry": {
#                 "type": "MultiPolygon",
#                 "coordinates": [
#                     [
#                         [
#                             [
#                                 8.617437378000091,
#                                 47.757318624000078
#                             ],
#                             [
#                                 8.629839721000053,
#                                 47.762796326000085
#                             ],
#                             [
#                                 8.635007365000149,
#                                 47.784603780000083
#                             ],
#                             [
#                                 8.644102417000113,
#                                 47.791011658000031
#                             ]
#                         ]
#                     ]
#                 ]
#             }
#         }
#     ]
# }, ggg.World['Earth'])

# # Create a land token
# land_token = ggg.LandToken.new(land, symbol="SOME_LAND", name="Some land")

# # Mint land tokens to the state's wallet
# land_token.mint(
#     state.wallet.get_address(land_token),
#     1000,
#     metadata={}
# )

# # Ownership checks
# try:
#     ck_btc.set_owner(alice)
# except Exception as e:
#     pass # TODO: need to figure out a way to pass the exception down to the result    

# # Capture the current system time
# t = get_system_time()

# # Import snapshot functionality and generate snapshots for the last 10 days
# for i in range(10):
#     take_snapshot(timestamp_to_date(t - i * DAY))

result = 'OK'
