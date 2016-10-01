from functools import wraps

from .models import User


def with_user(func):
    @wraps(func)
    def decorated(message, *args, **kwargs):
        user_id = message.body.get('user')
        if user_id is None:
            # maybe a bot
            return
        user, is_created = User.get_or_create(id=user_id)
        if is_created:
            user.save()
        return func(message, user, *args, **kwargs)
    return decorated
