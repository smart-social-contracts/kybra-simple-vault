from kybra import (
    CallResult,
    Principal,
    nat,
    blob,
    ic,
    Async,
    update,
    query,
)

from vault.constants import CKBTC_CANISTER
from vault.utils import parse_candid

from kybra_simple_logging import get_logger, save_var

logger = get_logger(__name__)
logger.set_level(logger.DEBUG)


def get_transactions(start: nat, length: nat) -> Async[str]:
    # Example: '(record { start = 2_324_900 : nat; length = 2 : nat })'
    candid_args = '(record { start = %s : nat; length = %s : nat })' % (start, length)
    ret = {
        'input': None,
        'output': None,
        'parsed_output': None,
        'error': None
    }

    ret['input'] = candid_args

    logger.debug('get_transactions(%s, %s)' % (start, length))
    try:
        call_result: CallResult[blob] = yield ic.call_raw(
            Principal.from_str(CKBTC_CANISTER),
            "get_transactions",
            ic.candid_encode(candid_args),
            0
        )
        ret['output'] = call_result
        logger.debug('get_transactions(%s, %s) (2): %s' % (start, length, call_result))

        if hasattr(call_result, 'Ok'):
            logger.debug('get_transactions(%s, %s) (3): %s' % (start, length, ic.candid_decode(call_result.Ok)))
            encoded_output = ic.candid_decode(call_result.Ok)
            save_var('encoded_output', encoded_output)
            ret['encoded_output'] = encoded_output
            parsed_output = parse_candid(encoded_output)
            save_var('parsed_output', parsed_output)
            ret['parsed_output'] = parsed_output
        else:
            logger.error('get_transactions(%s, %s) error: %s' % (start, length, call_result))
            ret['error'] = str(call_result)
    except Exception as e:
        logger.error('Exception in get_transactions(%s, %s): %s' % (start, length, str(e)))
        import traceback
        logger.error(traceback.format_exc())
        ret['error'] = str(e) + '\n' + traceback.format_exc()

    return ret
