import random
import traceback


class Tester:
    def __init__(self, test_class, logger=None):
        self.test_instance = test_class()
        self.log = print if not logger else logger

    def run_tests(self):
        """Run all test methods in the test class and report results."""
        test_methods = [
            getattr(self.test_instance, func)
            for func in dir(self.test_instance)
            if callable(getattr(self.test_instance, func)) and func.startswith("test_")
        ]
        random.shuffle(test_methods)  # catch hidden dependencies among tests
        failed = 0
        for test in test_methods:
            try:
                # Call setUp if it exists
                if hasattr(self.test_instance, "setUp"):
                    self.test_instance.setUp()
                test()
                self.log(f"\033[92m{test.__name__} passed\033[0m")  # Green for pass
            except Exception as e:
                self.log(f"\033[91m{test.__name__} failed: {e}\033[0m")  # Red for fail
                self.log(traceback.format_exc())
                failed += 1
        print(
            f"\033[91m{failed} tests failed\033[0m"
            if failed > 0
            else "\033[92mAll tests passed\033[0m"
        )
        return failed

    @classmethod
    def assert_raises(cls, exception, func, *args, **kwargs):
        """Assert that a function raises a specific exception."""
        try:
            func(*args, **kwargs)
        except exception:
            print(
                f"\033[92m{func.__name__} raised {exception.__name__} as expected\033[0m"
            )
            return True
        except Exception as e:
            print(f"\033[91m{func.__name__} raised an unexpected exception: {e}\033[0m")
            return False
        else:
            print(f"\033[91m{func.__name__} did not raise {exception.__name__}\033[0m")
            return False
