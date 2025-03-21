# gets to connect selected representative with a public openchat room



# from gcm.base import Token
# from gcm.core import Citizen, Tax, Governor, Representative, Voting, Treasury, Ministry
# from gcm.civil import Company
# from gcm.justice import Judiciary, Court, Judge, Case
# from gcm.resources import Land, Energy
# from gcm.registry.humans import WorldCoin, SwissId
# from gcm.welfare.health import Hospital, Doctor, Nurse
# from gcm.welfare.subsidy import Pension
# from gcm.finance import Currency, Bond, Stock

# state = State()

# def init_state(state):
#   state.name = "My New State"
#   state.description = "This is a new state"
#   state.map.polygons = [] # TODO
#   state.currencies = []
#   state.currencies.append(CurrencyWrapper('SBTC', Currency.BTC))
#   state.registry.identities = {
#     'WorldCoin': WorldCoin(),
#     'SwissId': SwissId()
#   }
#   public_justice_system = Judiciary(
#     supreme_court = True,
#     supreme_court_judges = []
#   ) # TODO: how are the judges elected
#   state.justice.systems = {
#     'public': public_justice_system
#   }

#   def currency_transfer(TransferRequest: transfer_request):
#     if transfer_request.transfer.currency.name == 'SBTC' and transfer_request.transfer.amount > 100 and all(state.ministries['Finance'].officials in transfer_request.approvals):
#       return True # all SBTC transfers of more than 100 BTC need approval from all officials of the ministry of finance
#     return False
#   state.currency['BTC'].hooks.transfer = currency_transfer

# def be_born(citizen: Citizen):
#   state.treasury.transfer(amount=0.001, ccy=Currency['SBTC'], to=[wallet for wallet in citizen.parents[0].wallets if wallet.currency.name == 'BTC'][0])

#   # check if we need to hire more doctors and nurses, professors, etc.

# def tax_wealth(citizen):
#   '''

#     Goes through all assets and charges a citizen

#   '''

#   # TODO

# def sign_off(citizen: Citizen):
#   tax_wealth(citizen, 0.5)

# State.initialize = init_state
# Citizen.events.be_born = be_born
# Citizen.hooks.sign_off = sign_off


