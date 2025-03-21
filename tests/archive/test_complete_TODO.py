import ggg
from pprint import pprint

# create 2 states
# state1 is switzerland
#   geographical division by cantons and municipalities
#   create the department of the state for each canton and municipality (parliament, health, education, justice)

# state2 is an archipielago in nordic sea

# create 100k users
# some of them belonging to both states
# some of them belonging to one state
# some of them don't belong to any state

# test AI models with cases:
#   1. citizen asks the governor to create a department
#   2. governor creates the department
#   3. citizen asks the governor to delete the department
#   4. governor deletes the department


ggg.base.initialize()
pprint(ggg.base.universe())

state = ggg.Organization.new('state')

print(state.to_dict())

print(50 * '*')
print(ggg.base.universe())


state.extension = '''def test_funtion(a="hola"):
    return a + ' world'
'''
state.save()

print(50 * '.')
pprint(state.to_dict())

print(state.run('test_funtion', 'a="hello"'))


alice = ggg.User.new('Alice', 'aaa')
state.token.mint(alice.wallet.address(state.token), 100)

print('state.wallet.address(BTC)', state.wallet.address(ggg.Token['BTC']))

print('alice balance', state.token.balance(alice.wallet.address(state.token)))
print('state balance', state.token.balance(state.wallet.address(state.token)))

state.token.transfer(alice.wallet.address(state.token), state.wallet.address(state.token), 10)
print('alice balance', state.token.balance(alice.wallet.address(state.token)))
print('state balance', state.token.balance(state.wallet.address(state.token)))

# print(50 * '*')
# pprint(ggg.base.universe())
