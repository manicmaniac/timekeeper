from io import StringIO
import os.path
import unittest
from unittest.mock import MagicMock, call, patch

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

    def test_safe_upload_file_with_text_file_in_public_channel(self):
        message = MagicMock()
        message.body.__getitem__.side_effect = (
            lambda key: 'CXXXXXXX' if key == 'channel' else None
        )
        filename = 'filename'
        path = 'path'
        comment = 'comment'
        safe_upload_file(message, filename, path, comment, is_text_file=True)
        message.channel.upload_file.assert_called_once_with(filename, path,
                                                            comment)

    def test_safe_upload_file_with_text_file_in_private_channel(self):
        message = MagicMock()
        message.body.__getitem__.side_effect = (
            lambda key: 'DXXXXXXX' if key == 'channel' else None
        )
        filename = 'filename'
        path = 'path'
        comment = 'comment'
        mock_open = MagicMock(return_value=StringIO('foo'))
        with patch('builtins.open', mock_open):
            safe_upload_file(message, filename, path, comment,
                             is_text_file=True)
        message.reply.assert_called_once_with('```\nfoo\n```')

    def test_safe_upload_file_with_binary_file_in_private_channel_fails(self):
        message = MagicMock()
        message.body.__getitem__.side_effect = (
            lambda key: 'DXXXXXXX' if key == 'channel' else None
        )
        filename = 'filename'
        path = 'path'
        comment = 'comment'
        safe_upload_file(message, filename, path, comment, is_text_file=False)
        reply_message = 'Sorry, I cannot upload a file in the private channel.'
        message.reply.assert_called_once_with(reply_message)

    def test_triple_backquoted(self):
        self.assertEqual('```\nfoo\n```', triple_backquoted('foo'))

    def test_triple_backquoted_raises_value_error_with_triple_backquotes(self):
        self.assertRaises(ValueError, triple_backquoted, '```')
