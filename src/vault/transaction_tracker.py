
import ast

def parse_candid(i: str) -> str:
    i = i.strip()
    i = i.replace('record {', '{')
    i = i.replace('opt', '')
    i = i.replace('blob', '')
    i = i.replace('vec', '')
    i = i.replace('principal', '')
    i = i.replace('null', 'None')
    i = i.replace(': nat64', '')
    i = i.replace(': nat', '')
    i = i.replace(';', '')
    i = i.replace('_', '')
    i = i.replace(' = ', ': ')
    i = i.replace('\x00', '')

    i2 = []
    is_inside_transactions = False
    level = 0
    lines = i.split('\n')
    for i, l in enumerate(lines):
        if is_inside_transactions:
            if '{' in l:
                level += 1
            if '}' in l:
                level -= 1
                if level < 0:
                    is_inside_transactions = False
                    l = ']'

        if '1349681965' in l:
            continue
        if '5094982' in l:
            continue
        if l == '}' and is_inside_transaction:
            l = ']'
        if '{' not in l and '(' not in l:
            if ',' not in l and i != len(lines) - 1:
                l += ','
        if '3331539157:  {' in l:
            l = '3331539157 : ['
            is_inside_transactions = True
            level = 0

        i2.append(l)

    i2 = '\n'.join(i2)

    field_map = {
        "1_779_015_299": "first_index",
        "2_799_807_105": "log_length",
        "3_331_539_157": "transactions",
        "3_650_848_786": "archived_transactions",
        "2_131_139_013": "callback",
        "2_215_343_202": "start",
        "2_668_074_214": "length",
        "2_781_795_542": "timestamp",
        "1_191_829_844": "kind",
        "3_573_748_184": "amount",
        "3_664_621_355": "transfer",
        "1_136_829_802": "from",
        "947_296_307": "owner",
        "25_979": "to",
    }

    for k, v in field_map.items():
        i2 = i2.replace(k.replace('_', ''), '"%s"' % v)

    print(i2)
    d = ast.literal_eval(i2)

    return d


class TransactionTracker:
    def __init__(self, principals: list[str]):
        self.log_length = 0
        self.transactions = []
        self.principals = principals
        self.ledger = {}

    def get_transactions(self):
        pass

    def parse_transactions(self):
        pass

    def update_ledger(self):
        pass

    @property
    def log_length(self):
        return self.log_length

    @property
    def transactions(self):
        return self.transactions

    @property
    def ledger(self):
        return self.ledger
