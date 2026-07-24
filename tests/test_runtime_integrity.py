from __future__ import annotations

import unittest

from qviraex.tests import test_runtime_integrity


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    del tests, pattern
    return loader.loadTestsFromModule(test_runtime_integrity)
