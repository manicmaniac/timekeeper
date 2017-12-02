from datetime import timedelta
import unittest

from timekeeper.utils import format_timedelta


class TestUtils(unittest.TestCase):
    def test_format_timedelta_parameterized(self):
        # (seconds, expected_value)
        parameters = [
            (36, '00:00:36'),
            (360, '00:06:00'),
            (3600, '01:00:00'),
            (36000, '10:00:00'),
            (24 * 60 * 60, '24:00:00'),
            (359999, '99:59:59'),
            (360000, '100:00:00'),
        ]
        for seconds, expected_value in parameters:
            actual_value = format_timedelta(timedelta(seconds=seconds))
            self.assertEqual(actual_value, expected_value)
