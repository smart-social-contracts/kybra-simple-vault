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
        transaction_tracker = TransactionTracker('vault', 0)
        transaction_tracker.check_transactions()

        d = app_data.to_dict()
        assert d['initial_index'] == 2328390
        assert d['log_length'] == 2328398
        assert d['vault_principal'] == 'vault'
        assert d['balance'] == 0
        assert d['total_inflow'] == 0
        assert d['total_outflow'] == 0

        return 0


def run():
    print("Running tests...")
    tester = Tester(TestBasic)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
