# """Tests for entity functionality in Kybra Simple DB."""

import asyncio
from tester import Tester

# from utils import parse_candid
# from logger import get_logger
# log = get_logger()
from entities import app_data, Transaction
from services import TransactionTracker
from kybra_simple_db import *

class TestBasic:
    async def test_basic(self):
        app_data().vault_principal = 'aaaa-test'
        transaction_tracker = TransactionTracker()
        yield transaction_tracker.check_transactions()

        d = app_data().to_dict()
        print('d', d)
        assert d['first_processed_index'] == 0
        assert d['last_processed_index'] == 2328395

        yield transaction_tracker.check_transactions()
        d = app_data().to_dict()
        print('111111111111 d', d)
        assert d['first_processed_index'] == 2328395
        assert d['last_processed_index'] == 2328398

        print('222222222222 d', d)
        print(Database.get_instance().dump_json(pretty=True))

        # check number of transactions and their values
        # check balances

        return 0


async def run():
    print("Running tests...")
    tester = Tester(TestBasic)
    return await tester.run_tests()


if __name__ == "__main__":
    exit(asyncio.run(run()))
