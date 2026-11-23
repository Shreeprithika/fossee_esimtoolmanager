"""
Master Test Runner for eSim Automated Tool Manager
Runs all unit and integration tests across the test suite.
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_all_tests():
    print("=" * 70)
    print(" Running eSim Automated Tool Manager Test Suite")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Errors:    {len(result.errors)}")
    print(f"Failures:  {len(result.failures)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
