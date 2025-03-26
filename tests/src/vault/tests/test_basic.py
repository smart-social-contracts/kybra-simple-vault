# """Tests for entity functionality in Kybra Simple DB."""

import ast

from tester import Tester

from utils import parse_candid
# from logger import get_logger
# log = get_logger()
from entities import app_data
from services import TransactionTracker

class TestBasic:
    def test_basic(self):
        print('app_data', app_data.to_dict())

        transaction_tracker = TransactionTracker('vault', 0)
        transaction_tracker.check_transactions()

        print('app_data', app_data.to_dict())

        return 0


def run():
    print("Running tests...")
    tester = Tester(TestBasic)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
