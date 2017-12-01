import errno
import logging
import os
import socket

from slackbot.bot import Bot


class LockFileExistsError(Exception):
    pass


def create_lock_file(path):
    try:
        with open(path, 'x') as f:
            pid = os.getpid()
            f.write(str(pid) + '\n')
    except IOError as e:
        if e.errno == errno.EEXIST:
            message = 'Lock file at {path} exists.'.format(path=path)
            raise LockFileExistsError(message) from e
        raise e


def remove_lock_file(path):
    with open(path, 'r') as f:
        data = f.read().rstrip()
    if data.isdigit():
        saved_pid = int(data)
        pid = os.getpid()
        if pid == saved_pid:
            os.unlink(path)


def main():
    path = os.path.join(os.path.dirname(__file__), '.timekeeper.pid')
    try:
        create_lock_file(path)
    except LockFileExistsError as e:
        logging.error('Failed to acquire lock {} becuse {}'.format(path, e))
    else:
        logging.info('Acquired lock {}'.format(path))
        bot = Bot()
        bot.run()
    finally:
        remove_lock_file(path)


if __name__ == '__main__':
    main()
