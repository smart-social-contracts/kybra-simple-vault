# This file servers to create a demo state. These are the commands to install it to the system:
# Running on an IC server:    dfx canister call canister_main run_code "$(cat tests/scenarios/demo/demo_extension.py)"
# Running on regular server:  curl -X POST -H "Content-Type: application/json" --data-binary "@tests/scenarios/demo/demo_extension.py" http://localhost:8000/run_code

'''
'''

import ggg
import math
from datetime import datetime, timedelta
from core.system_time import get_system_time, DAY, set_system_time


last_heartbeat = None  # To track daily executions

def initialize_state():
    # Constants for the simulation
    NUM_CITIZENS = 10000
    INITIAL_CITIZEN_COINS = 100  # Initial coins per citizen
    STATE_INITIAL_COINS = 1000000  # Initial state reserve
    MIN_DAILY_INCOME = 10  # Minimum daily income
    MAX_DAILY_INCOME = 1000  # Maximum daily income
    MIN_DAILY_EXPENSE = 5  # Minimum daily expense
    MAX_DAILY_EXPENSE = 500  # Maximum daily expense
    TAX_BRACKETS = [  # (income_threshold, tax_rate)
        (100, 0.10),   # 10% tax for income up to 100
        (500, 0.20),   # 20% tax for income between 100 and 500
        (1000, 0.30),  # 30% tax for income above 500
    ]
    WELFARE_THRESHOLD = 50  # Citizens with daily income below this get welfare
    WELFARE_AMOUNT = 25  # Daily welfare amount per eligible citizen

    # Create the main state organization
    state = ggg.Organization.new('Social State')
    government = ggg.Organization.new('Government')
    tax_department = ggg.Organization.new('Tax Department')
    welfare_department = ggg.Organization.new('Welfare Department')

    # Link the organizations
    state.add_member(government)
    government.add_member(tax_department)
    government.add_member(welfare_department)

    # # Create the state coin
    # coin = ggg.Token.new('COIN', token_core=ggg.TokenInternal)
    
    # # Initialize state wallet with coins
    # coin.mint(state.wallet.get_address(coin), STATE_INITIAL_COINS)
    
    # Create land entity with predefined GeoJSON
    land = ggg.Land.new({
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
                                    8.635007365000149,
                                    47.784603780000083
                                ],
                                [
                                    8.644102417000113,
                                    47.791011658000031
                                ]
                            ]
                        ]
                    ]
                }
            }
        ]
    }, ggg.World['Earth'])

    # Create a land token
    land_token = ggg.LandToken.new(land, symbol="SOME_LAND", name="Some land")

    # Mint land tokens to the state's wallet
    land_token.mint(
        state.wallet.get_address(land_token),
        1000,
        metadata={}
    )
    
    # Create citizens and assign initial coins
    citizens = []  
    for i in range(NUM_CITIZENS):
        citizen = ggg.User.new(f'Citizen_{i}', f'identity_{i}')
        state.add_member(citizen)
        citizens.append(citizen)
        coin.mint(citizen.wallet.get_address(coin), INITIAL_CITIZEN_COINS)
        
        # Store initial attributes for the citizen
        base_income = MIN_DAILY_INCOME + (MAX_DAILY_INCOME - MIN_DAILY_INCOME) * (i / NUM_CITIZENS)
        citizen.daily_income = base_income
        citizen.tax_debt = 0  # Initialize tax debt
    
    return state, coin, citizens, {
        'MIN_DAILY_INCOME': MIN_DAILY_INCOME,
        'MAX_DAILY_INCOME': MAX_DAILY_INCOME,
        'MIN_DAILY_EXPENSE': MIN_DAILY_EXPENSE,
        'MAX_DAILY_EXPENSE': MAX_DAILY_EXPENSE,
        'TAX_BRACKETS': TAX_BRACKETS,
        'WELFARE_THRESHOLD': WELFARE_THRESHOLD,
        'WELFARE_AMOUNT': WELFARE_AMOUNT
    }

def calculate_tax(income, tax_brackets):
    """Calculate tax based on income brackets"""
    tax = 0
    remaining_income = income
    
    for threshold, rate in tax_brackets:
        if remaining_income <= 0:
            break
        taxable_amount = min(remaining_income, threshold)
        tax += taxable_amount * rate
        remaining_income -= taxable_amount
    
    return tax

def simulate_daily_activities(citizen, coin, config, day_number):
    """Simulate daily income and expenses for a citizen"""
    # Generate daily income with some variation based on day number
    variation = math.sin(day_number / 7) * 0.2  # 20% variation over a weekly cycle
    daily_income = citizen.daily_income * (1 + variation)
    
    # Generate daily expenses (about 60% of income with some variation)
    expense_ratio = 0.6 + math.sin(day_number / 30) * 0.1  # Varies between 50-70% over monthly cycle
    daily_expense = daily_income * expense_ratio
    daily_expense = max(config['MIN_DAILY_EXPENSE'], 
                       min(config['MAX_DAILY_EXPENSE'], daily_expense))
    
    # Update citizen's wallet
    citizen.wallet.deposit(coin, daily_income)
    citizen.wallet.withdraw(coin, daily_expense)
    
    return daily_income

heartbeat_hook_source = '''def heartbeat_hook():
    # print('heartbeat 1')

    global last_heartbeat
    current_time = datetime.now()
    
    # Only run once per day
    if last_heartbeat and (current_time - last_heartbeat).days < 1:
        return 0
    
    # Calculate day number (for cyclic variations)
    day_number = (current_time - datetime(2025, 1, 1)).days
    
    last_heartbeat = current_time
    state = ggg.Organization.get('Social State')
    coin = ggg.Token.get('COIN')
    
    # Get simulation configuration
    config = getattr(state, 'simulation_config', {
        'MIN_DAILY_INCOME': 10,
        'MAX_DAILY_INCOME': 1000,
        'MIN_DAILY_EXPENSE': 5,
        'MAX_DAILY_EXPENSE': 500,
        'TAX_BRACKETS': [(100, 0.10), (500, 0.20), (1000, 0.30)],
        'WELFARE_THRESHOLD': 50,
        'WELFARE_AMOUNT': 25
    })
    
    # Daily simulation for each citizen
    tax_collection = 0
    welfare_recipients = []
    
    for citizen in state.members:
        if isinstance(citizen, ggg.User):
            # Simulate daily activities
            daily_income = simulate_daily_activities(citizen, coin, config, day_number)
            
            # Calculate and collect tax
            daily_tax = calculate_tax(daily_income, config['TAX_BRACKETS']) + citizen.tax_debt
            wallet_balance = citizen.wallet.get_balance(coin)
            
            if wallet_balance >= daily_tax:
                citizen.wallet.transfer(coin, state.wallet.get_address(coin), daily_tax)
                tax_collection += daily_tax
                citizen.tax_debt = 0
            else:
                # If can't pay full tax, pay what they can and accumulate debt
                if wallet_balance > 0:
                    citizen.wallet.transfer(coin, state.wallet.get_address(coin), wallet_balance)
                    tax_collection += wallet_balance
                    citizen.tax_debt = daily_tax - wallet_balance
                else:
                    citizen.tax_debt = daily_tax
            
            # Check for welfare eligibility
            if daily_income < config['WELFARE_THRESHOLD']:
                welfare_recipients.append(citizen)
    
    # Distribute welfare
    if welfare_recipients:
        total_welfare = len(welfare_recipients) * config['WELFARE_AMOUNT']
        state_balance = state.wallet.get_balance(coin)
        
        if state_balance >= total_welfare:
            # Distribute welfare equally
            for recipient in welfare_recipients:
                state.wallet.transfer(coin, recipient.wallet.get_address(coin), config['WELFARE_AMOUNT'])
    
    return 0
'''

# Initialize the state
state, coin, citizens, config = initialize_state()
# state.simulation_config = config

# # Create the source code string for the platform
# source_code = f"""
# def heartbeat_hook():
# {inspect.getsource(heartbeat_hook)}
# """

# print('source_code')
# print('"""')
# print(source_code)
# print('"""')

# Save the extension code to the platform
state.extension = heartbeat_hook_source
state.save()

# Create a new proposal with code
proposal_code = """
print('Hello World!!!')
""".strip()
now = get_system_time()
proposal = ggg.Proposal.new(
    "Proposal to increase budget", proposal_code, now)

# Submit the proposal to the state and have Bob vote on it
proposal.submit(state)

for citizen in citizens[:len(citizens)//2]:
    proposal.vote(citizen.wallet.get_address(state.token), ggg.Proposal.VOTING_YAY)

# Advance time to ensure the proposal deadline has passed
set_system_time(now + DAY)

# Check proposals and update state if necessary
state.check_proposals()
