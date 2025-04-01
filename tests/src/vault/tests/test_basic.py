# """Tests for entity functionality in Kybra Simple DB."""

import asyncio
from unittest.mock import patch
from entities import app_data
from services import TransactionTracker
from kybra_simple_db import *

async def test_basic():
    # Reset app_data to initial state
    app_data_instance = app_data()
    app_data_instance.first_processed_index = 0
    app_data_instance.last_processed_index = 0
    app_data_instance.vault_principal = 'aaaa-test'
    
    # Print initial state
    print('Initial state:', app_data_instance.to_dict())
    
    # First test - verify initial values
    d = app_data_instance.to_dict()
    assert d['first_processed_index'] == 0
    assert d['last_processed_index'] == 0
    
    # Second test - manually set values and verify
    app_data_instance.first_processed_index = 2328392
    app_data_instance.last_processed_index = 2328398
    
    # Print and verify the updated values
    d = app_data_instance.to_dict()
    print('Updated state:', d)
    assert d['first_processed_index'] == 2328392
    assert d['last_processed_index'] == 2328398
        
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
