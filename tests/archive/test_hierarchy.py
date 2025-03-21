import ggg
from pprint import pprint

ggg.base.initialize()
pprint(ggg.base.universe())

state = ggg.Organization.new('state')
# ministy_1 = ggg.Organization.new('ministy_1')
# ministy_2 = ggg.Organization.new('ministy_2')
# department_1 = ggg.Organization.new('department_1')
# department_2 = ggg.Organization.new('department_2')


# ministy_1.join(state)
# ministy_2.join(state)
# department_1.join(ministy_1)
# department_2.join(ministy_2)


# pprint(state.to_dict())
# pprint(ministy_1.to_dict())

print('state.wallet.address(state.token)', state.wallet.address(state.token))
print(state.token.balance(state.wallet.address(state.token)))
state.token.mint(state.wallet.address(state.token), 1000)

print(state.token.balance(state.wallet.address(state.token)))


print(50 * '*')
pprint(ggg.base.universe())
