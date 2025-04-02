
def get_transactions(start: int, length: int) -> str:
    print('** get_transactions', start, length)
    if start == 0:
        return {
            'error': None,
            'parsed_output': {
                'first_index': 2328300,
                'log_length': 2328395,
                'transactions': [], 'archived_transactions': []}
        }
    else:
        return {'error': None, 'parsed_output': {'first_index': 2328395,
                'log_length': 2328398,
                                                 'transactions': [
                                                     {1092621391: None,
                                                      'kind': 'transfer',
                                                      1214008994: None,
                                                      1378506061: None,
                                                      'timestamp': 1742840332822818232,
                                                      'transfer': {
                                                          'to': {'owner': 'aaaa-test'},  # vault canister
                                                          'from': {'owner': 'ztwhb-qiaaa-aaaaj-azw7a-cai'},
                                                          1213809850: None,
                                                          3258775938: None,
                                                          'amount': 908977,
                                                          3868658507: None}},
                                                     {1092621391: None,
                                                         'kind': 'transfer',
                                                         1214008994: None,
                                                         1378506061: None,
                                                         'timestamp': 1742840334069599178,
                                                         'transfer': {
                                                             'to': {'owner': 'ztwhb-qiaaa-aaaaj-azw7a-cai'},
                                                             'from': {'owner': 'aaaa-test'},  # vault canister
                                                             1213809850: None,
                                                             3258775938: None,
                                                             'amount': 447890,
                                                             3868658507: None}},

                                                     # to be ignored as neither `to` not `from` are the vault canister
                                                     {1092621391: None,
                                                         'kind': 'transfer',
                                                         1214008994: None,
                                                         1378506061: None,
                                                         'timestamp': 1742840639059074036,
                                                         'transfer': {
                                                             'to': {'owner': 'rtpxn-77ite-cm6ta-qh5te-pdqj6-ugxwe-dncpt-ewp7c-nui4j-cpvwp-oae'},
                                                             'from': {'owner': 'xmiu5-jqaaa-aaaag-qbz7q-cai'},
                                                             1213809850: '\x05\x068',
                                                             3258775938: None,
                                                             'amount': 1236274,
                                                             3868658507: None}}
                                                 ], 'archived_transactions': []}
                }
