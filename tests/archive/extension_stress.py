# PYTHONPATH=src/canister_main python tests/extension_stress.py

import ggg

NUM_CITIZENS_PER_STATE = 100
NUM_STATES = 1

for s_index in range(NUM_STATES):
    state = ggg.State('State %d' % s_index)
    state.commit()
    # print(state.name)
    for c_index in range(NUM_CITIZENS_PER_STATE):
        name = 'State %d Citizen %d' % (s_index, c_index)
        citizen = ggg.Citizen(name)
        citizen.commit()
        citizen.join_state(state)

result = str('')
