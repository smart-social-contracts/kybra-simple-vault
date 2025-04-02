# """Tests for entity functionality in Kybra Simple DB."""

import asyncio
from unittest.mock import patch
from entities import app_data
from services import TransactionTracker, reset
from kybra_simple_db import *
from kybra_simple_logging import get_logger, set_log_level
from utils_icp import get_transactions
from vault.constants import TRANSACTION_BATCH_SIZE

logger = get_logger(__name__)
logger.set_level(logger.DEBUG)


async def run_generator(gen):
    """Helper function to run a generator as if it were an async function"""
    try:
        # Get first yielded value from the generator
        yielded = next(gen)

        # Process the generator until it's done
        while True:
            try:
                # In the Kybra pattern, check_transactions will yield get_transactions(arg1, arg2)
                # Since this is a function call and not the result, we need to:
                # 1. Check what was yielded (usually a function reference)
                # 2. Call our mocked function with the same args
                # 3. Send that result back into the generator

                # Most yielded values in this codebase will be function references
                if not app_data().log_length:
                    # First call to get_transactions is with (0, 1)
                    mock_response = get_transactions(0, 1)
                    logger.debug("Sending mock response for get_transactions(0, 1)")
                else:
                    # Second call will use the last_processed_index
                    mock_response = get_transactions(app_data().log_length, TRANSACTION_BATCH_SIZE)
                    logger.debug(f"Sending mock response for get_transactions({app_data().log_length}, {TRANSACTION_BATCH_SIZE})")

                # Send the mock response back to the generator
                yielded = gen.send(mock_response)
            except StopIteration as e:
                return e.value
    except StopIteration as e:
        return e.value


async def test_basic():

    for i in range(3):
        # Reset app_data to initial state
        app_data_instance = app_data()
        app_data_instance.log_length = 0
        app_data_instance.last_processed_index = 0
        app_data_instance.vault_principal = 'aaaa-test'

        # Create transaction tracker and run the actual method
        transaction_tracker = TransactionTracker()

        # Print initial state
        logger.debug('Initial state: %s' % app_data_instance.to_dict())
        d = app_data_instance.to_dict()
        assert d['log_length'] == 0
        assert d['last_processed_index'] == 0

        # The run_generator function will interact with app_data() directly

        # Run the first check_transactions call - should set up basic state
        result = await run_generator(transaction_tracker.check_transactions())
        logger.debug('First check_transactions result: %s' % result)

        d = app_data().to_dict()
        logger.debug('After first check: %s' % d)
        assert d['log_length'] == 2328395
        assert d['last_processed_index'] == 0

        # Run the second check_transactions call
        result = await run_generator(transaction_tracker.check_transactions())
        logger.debug('Second check_transactions result: %s' % result)

        d = app_data().to_dict()
        logger.debug('After second check: %s' % d)
        assert d['log_length'] == 2328398
        assert d['last_processed_index'] == 2328397

        # Print database contents
        logger.debug('Database dump: %s' % Database.get_instance().dump_json(pretty=True))

        # check number of transactions and their values
        # check balances

        # Run reset
        reset()
        
        # Print final state
        logger.debug('Final state: %s' % app_data().to_dict())
        d = app_data().to_dict()
        assert d['log_length'] == 0
        assert d['last_processed_index'] == 0



async def run():
    return await test_basic()


if __name__ == '__main__':
    import asyncio
    asyncio.run(run())
