from functools import wraps

from timekeeper.models import User


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
        if user.name is None:
            user_info = message._client.webapi.users.info(user_id)
            if not user_info.successful:
                raise RuntimeError(user_info.error)
            name = user_info.body['user']['name']
            user.name = name
            user.save()
        return func(message, user, *args, **kwargs)
    return decorated
