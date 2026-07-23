from __future__ import annotations

import unittest

from qviraex.tests import test_integrity_atomicity_numeric


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    del tests, pattern
    return loader.loadTestsFromModule(test_integrity_atomicity_numeric)
