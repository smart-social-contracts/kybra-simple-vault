from ggg import *  # comment his line out before deploying


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


# onboarding of current states into the platform => JJ

# Spain:

# Switzerland:

# Lugano o Zug
