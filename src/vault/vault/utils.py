import ast
import traceback

from kybra_simple_logging import get_logger

logger = get_logger(__name__)


def parse_candid(input: str) -> str:
    input = input.strip()
    input = input.replace('record {', '{')
    input = input.replace('opt', '')
    input = input.replace('blob', '')
    input = input.replace('vec', '')
    input = input.replace('principal', '')
    input = input.replace('null', 'None')
    input = input.replace(': nat64', '')
    input = input.replace(': nat', '')
    input = input.replace(';', '')
    input = input.replace('_', '')
    input = input.replace(' = ', ': ')
    input = input.replace('\x00', '')

    output = []
    is_inside_transactions = False
    level = 0
    lines = input.split('\n')
    for i, l in enumerate(lines):
        if '2131139013' in l:
            continue
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
        if '3331539157:  {}' in l:
            l = '3331539157 : [],'
        elif '3331539157:  {' in l:
            l = '3331539157 : ['
            is_inside_transactions = True
            level = 0

        if '3650848786:  {}' in l:
            l = '3650848786 : [],'
        elif '3650848786:  {' in l:
            l = '3650848786 : ['
            is_inside_transactions = True
            level = 0

        output.append(l)

    output = '\n'.join(output)

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
        output = output.replace(k.replace('_', ''), '"%s"' % v)

    try:
        d = ast.literal_eval(output)
        return d[0]
    except Exception as e:
        logger.error('Error parsing candid: %s' % e)
        logger.error('*** Input message:\n%s' % input)
        logger.error('*** Output message:\n%s' % output)
        logger.error('*** Traceback:\n%s' % traceback.format_exc())
        raise e

