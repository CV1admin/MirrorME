from __future__ import annotations

import unittest

from qviraex.tests import test_mkultra_v03


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    del tests, pattern
    return loader.loadTestsFromModule(test_mkultra_v03)
