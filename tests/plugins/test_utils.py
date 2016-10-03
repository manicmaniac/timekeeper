import os.path
import unittest

from timekeeper.plugins.utils import (create_temp_dir, is_direct_message,
                                      safe_upload_file, triple_backquoted)


class TestUtils(unittest.TestCase):
    def test_create_temp_dir(self):
        with create_temp_dir() as temp_dir:
            self.assertTrue(os.path.isdir(temp_dir))
        self.assertFalse(os.path.isdir(temp_dir))

    def test_is_direct_message(self):
        self.assertTrue(is_direct_message('DXXXXXXX'))
        self.assertFalse(is_direct_message('CXXXXXXX'))
        self.assertFalse(is_direct_message('PXXXXXXX'))

    def test_triple_backquoted(self):
        self.assertEqual('```\nfoo\n```', triple_backquoted('foo'))
