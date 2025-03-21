from ggg import State, User, Citizen, Proposal, User

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


Citizen.new(User["DEFAULT"]).state_join(state)

Citizen.new(User.new("Alice", "aaa-1")).state_join(state)

Citizen.new(User.new("Bob", "aaa-2")).state_join(state)

proposal = Proposal.new("title", "result = organization", get_system_time())
proposal.submit(state.organization)

set_caller(User["Bob"].address)
proposal.vote(Proposal.VOTING_YAY)

t = get_system_time()
for i in range(10):
    take_snapshot(timestamp_to_date(t - i * DAY))

result = "OK"
