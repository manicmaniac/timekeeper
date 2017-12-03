import unittest
from unittest.mock import MagicMock, patch

from timekeeper.models import User
from timekeeper.plugins.decorators import with_user


class TestDecorators(unittest.TestCase):
    def test_with_user_when_message_does_not_have_user(self):
        func = with_user(lambda message, user: user)
        message = MagicMock()
        message.body.get = lambda key: None
        self.assertIsNone(func(message))

    def test_with_user_when_message_has_existent_user(self):
        func = with_user(lambda message, user: user)
        mock_user_info = MagicMock(successful=True)
        mock_user_info.__getitem__.side_effect = (
            lambda key: {'name': 'name'} if key == 'user' else {}
        )
        message = MagicMock()
        message.configure_mock(**{
            'body.get': lambda key: 'id' if key == 'user' else None,
            '_client.webapi.users.info': lambda user_id: mock_user_info,
        })
        mock_user = MagicMock(name='name')
        with patch.object(User, 'get_or_create', lambda id: (mock_user, False)):
            self.assertEqual(func(message), mock_user)

    def test_with_user_when_message_has_nonexistent_user(self):
        func = with_user(lambda message, user: user)
        mock_user_info = MagicMock(successful=True)
        mock_user_info.__getitem__.side_effect = lambda key: None
        message = MagicMock()
        message.configure_mock(**{
            'body.get': lambda key: 'id' if key == 'user' else None,
            '_client.webapi.users.info': lambda user_id: mock_user_info,
        })
        mock_user = MagicMock(name=None)
        with patch.object(User, 'get_or_create', lambda id: (mock_user, True)):
            self.assertEqual(func(message), mock_user)
