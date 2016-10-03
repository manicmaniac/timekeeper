from datetime import timedelta
import unittest

from timekeeper.utils import format_timedelta


class TestUtils(unittest.TestCase):
    def test_format_timedelta(self):
        result = format_timedelta(timedelta(seconds=36))
        self.assertEqual('00:00:36', result)

        result = format_timedelta(timedelta(seconds=360))
        self.assertEqual('00:06:00', result)

        result = format_timedelta(timedelta(seconds=3600))
        self.assertEqual('01:00:00', result)

        result = format_timedelta(timedelta(seconds=36000))
        self.assertEqual('10:00:00', result)
