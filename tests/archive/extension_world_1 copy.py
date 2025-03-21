# from class_model.world import World
# from class_model.state import State
# from class_model.organization import Organization
# from class_model.proposal import Proposal
# from class_model.wallet import Wallet
# from core.objects import Token
# from class_model.user import User, Citizen

state = State.new(
    "State A",
    extension_source_code="""
                  
def constitute(state: State):
    print('Constituting new state "%s"' % state.id)
    token = state.organization.token
    token.name = "Citizenship Token"


def hook_new_citizen(state: State, user: User):
    print("hello from hook_new_citizen: " + str(user))
    state.organization.token.mint(user.address, 1)
    # examples of usage:
    # needs approval to join
    # needs to pay
    return "all good"
                  
""",
)

# extension_source_code="\n".join(
#     open(r"tests/modern_democracy/extension_state_1.py").read().split("\n")[1:]
# ),

Citizen.new(User["DEFAULT"]).state_join(state)

Citizen.new(User.new("Alice", "aaa-1")).state_join(state)

# state.organization.spinoff("tax department")
# state.organization.spinoff("infrastructures department")

Citizen.new(User.new("Bob", "aaa-2")).state_join(state)

proposal = Proposal.new("title", "result = organization", get_system_time())
proposal.submit(state.organization)

set_caller(User["Bob"].address)
proposal.vote(Proposal.VOTING_YAY)

t = get_system_time()
for i in range(10):
    take_snapshot(timestamp_to_date(t - i * DAY))

result = "OK"


# import class_model as Wold, State, User, Citizen


# world = ggg.World('Middle Earth')

# hobitton = ggg.State('Hobitton')


# class MyState(State):
#     MINIMUM_BALANCE = 1000
#     JOIN_FEE = 10

#     def new_citizen_joining(user: User):
#         if user in self.citizens():
#             raise Exception('User is already a citizen')

#         if
