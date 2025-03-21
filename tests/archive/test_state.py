

import stats.snapshot


def _run(SWISS_GEOJSON):
    # import time
    # Import necessary modules and functions
    import ggg  # Main module for generalized governance graph
    from pprint import pprint  # Pretty-print for better readability of outputs
    from core.system_time import get_system_time, timestamp_to_date, DAY  # Time utilities
    # from ggg.base import set_caller  # Function to set the caller identity

    # # Uncomment to initialize the GGG base and print the universe state
    # ggg.base.initialize()
    # pprint(ggg.base.universe())

    # Create the main state organization
    state = ggg.Organization.new('state')

    # Create primary branches of government
    congress = ggg.Organization.new('Congress')
    government = ggg.Organization.new('Government')
    supreme_court = ggg.Organization.new('Supreme Court')

    # Create ministries under the government
    ministy_economy = ggg.Organization.new('Ministry of Economy')
    ministy_security = ggg.Organization.new('Ministry of Security')
    ministy_education = ggg.Organization.new('Ministry of Education')

    # Create departments under respective ministries
    tax_department = ggg.Organization.new('Tax Department')
    police_department = ggg.Organization.new('Police Department')
    school_department = ggg.Organization.new('School Department')

    # Link the branches of government to the state
    congress.join(state)
    government.join(state)
    supreme_court.join(state)

    # Link ministries to the government
    ministy_economy.join(government)
    ministy_security.join(government)
    ministy_education.join(government)

    # Link departments to their respective ministries
    tax_department.join(ministy_economy)
    police_department.join(ministy_security)
    school_department.join(ministy_education)

    # Create users and assign identities
    alice = ggg.User.new('Alice', 'alice_identity')
    bob = ggg.User.new('Bob', 'bob_identity')

    # # Uncomment to print all token instances for debugging
    # pprint([i.to_dict() for i in ggg.Token.instances()])

    # Join users to the state
    alice.join(state)
    bob.join(state)

    # # Uncomment to print all token instances after joining users
    # pprint([i.to_dict() for i in ggg.Token.instances()])

    # Fetch the BTC token
    btc = ggg.Token['BTC']

    # Mint BTC tokens to the state wallet and transfer to users
    btc.mint(state.wallet.address(btc), 10000)
    btc.transfer(state.wallet.address(btc), alice.wallet.address(btc), 100)
    btc.transfer(state.wallet.address(btc), bob.wallet.address(btc), 100)

    # # Uncomment to print the universe state for debugging
    # # pprint(ggg.base.universe())

    # Create a new proposal with code
    proposal_code = """
    print('Hello World!!!')
    """.strip()
    proposal = ggg.Proposal.new("Proposal to increase budget", proposal_code, get_system_time())

    # Submit the proposal to the state and have Bob vote on it
    proposal.submit(state)
    # set_caller(ggg.User["Bob"].principal)  # Set Bob as the caller
    proposal.vote(bob.wallet.address(state.token), ggg.Proposal.VOTING_YAY)

    # # Uncomment to simulate a delay (e.g., for proposal processing)
    # time.sleep(1)

    # Check proposals and update state if necessary
    state._check_proposals()

    # # Uncomment to inspect various instances for debugging
    # pprint([i.to_dict() for i in ggg.Organization.instances()])
    # pprint([i.to_dict() for i in ggg.Token.instances()])
    # pprint([i.to_dict() for i in ggg.Proposal.instances()])

    # # Inspect Earth entity
    # pprint(ggg.World['Earth'].to_dict())

    # Create land representing Switzerland using a local GeoJSON file
    # switzerland_land = ggg.Land.new(open(r'/home/user/dev/the_project/app/tests/fixtures/switzerland.geojson').read(), ggg.World['Earth'])

    # Alternatively, fetch Switzerland GeoJSON from a remote URL
    # url = 'https://raw.githubusercontent.com/Batou125/the_project2a/63ef8a7d2f577dca0fb4f82169a143c23b27edcd/app/tests/fixtures/switzerland.geojson?token=GHSAT0AAAAAAC4XKWQ3DJG2VDPBWWQW4MHGZ4M2VQQ'
    # switzerland_land = ggg.Land.new(requests.get(url).text, ggg.World['Earth'])

    # Create Switzerland land entity with predefined GeoJSON
    switzerland_land = ggg.Land.new(SWISS_GEOJSON, ggg.World['Earth'])

    # Create a land token for Switzerland
    land_token = ggg.LandToken.new(switzerland_land, symbol="Switzerland", name="Land of Switzerland")

    # Mint land tokens to the state's wallet
    land_token.mint(
        state.wallet.address(land_token),
        1000,
        metadata={}
    )

    # # Uncomment to print land token details for debugging
    # pprint(land_token.to_dict())

    # # Uncomment to print land details for debugging
    # pprint(land_token.land.to_dict())

    # Capture the current system time
    t = get_system_time()

    # Import snapshot functionality and generate snapshots for the last 10 days
    from stats.snapshot import take_snapshot
    for i in range(10):
        take_snapshot(timestamp_to_date(t - i * DAY))

    # Inspect snapshots created for statistical analysis
    import stats
    pprint([i.to_dict() for i in stats.snapshot.Snapshot.instances()])


def run():
    SWISS_GEOJSON = '''
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "CHE",
                "properties": {
                    "name": "Switzerland"
                },
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [
                                    8.617437378000091,
                                    47.757318624000078
                                ],
                                [
                                    8.629839721000053,
                                    47.762796326000085
                                ],
                                [
                                    8.607618856000101,
                                    47.762253723000129
                                ],
                                [
                                    8.617437378000091,
                                    47.757318624000078
                                ]
                            ]
                        ]
                    ]
                }
            }
        ]
    }
    '''.strip()

    _run(SWISS_GEOJSON)
