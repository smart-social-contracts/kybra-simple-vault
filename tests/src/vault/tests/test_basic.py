# """Tests for entity functionality in Kybra Simple DB."""

import asyncio
from unittest.mock import patch
from entities import app_data
from services import TransactionTracker
from kybra_simple_db import *

from utils_icp import get_transactions


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
                if not app_data().last_processed_index:
                    # First call to get_transactions is with (0, 1)
                    mock_response = get_transactions(0, 1)
                    print("Sending mock response for get_transactions(0, 1)")
                else:
                    # Second call will use the last_processed_index
                    index = app_data().last_processed_index
                    mock_response = get_transactions(index, 10)  # assuming TRANSACTION_BATCH_SIZE is 10
                    print(f"Sending mock response for get_transactions({index}, 10)")

                # Send the mock response back to the generator
                yielded = gen.send(mock_response)
            except StopIteration as e:
                return e.value
    except StopIteration as e:
        return e.value


async def test_basic():
    # Reset app_data to initial state
    app_data_instance = app_data()
    app_data_instance.log_length = 0
    app_data_instance.last_processed_index = 0
    app_data_instance.vault_principal = 'aaaa-test'

    # Create transaction tracker and run the actual method
    transaction_tracker = TransactionTracker()

    # Print initial state
    print('Initial state:', app_data_instance.to_dict())
    d = app_data_instance.to_dict()
    assert d['log_length'] == 0
    assert d['last_processed_index'] == 0

    # Run the first check_transactions call - should set up basic state
    result = await run_generator(transaction_tracker.check_transactions())
    print('First check_transactions result:', result)

    d = app_data_instance.to_dict()
    print('After first check:', d)
    assert d['log_length'] == 2328395
    assert d['last_processed_index'] == 0

    # Run the second check_transactions call
    result = await run_generator(transaction_tracker.check_transactions())
    print('Second check_transactions result:', result)

    d = app_data_instance.to_dict()
    print('After second check:', d)
    assert d['log_length'] == 2328398
    assert d['last_processed_index'] == 2328397

    # Print database contents
    print('Database dump:')
    print(Database.get_instance().dump_json(pretty=True))

    # check number of transactions and their values
    # check balances


async def run():
    return await test_basic()


if __name__ == '__main__':
    import asyncio
    asyncio.run(run())
