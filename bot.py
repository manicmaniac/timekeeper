import errno
import logging
import os
import socket

from slackbot.bot import Bot

_lock_socket = None


class CannotCreateLockSocketError(Exception):
    pass


class LockSocketExistsError(Exception):
    pass


class LockFileExistsError(Exception):
    pass


def create_lock_socket():
    """
    Create and connect to an abstract socket to acquire system-wide lock.
    It is safer than lock file strategy but works only on a Linux system.
    """
    global _lock_socket
    _lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    lock_id = 'timekeeper-slackbot'
    try:
        _lock_socket.bind('\0' + lock_id)
    except socket.error as e:
        if e.errno == errno.ENOENT:
            message = 'Cannot create lock on a non-Linux system'
            raise CannotCreateLockSocketError(message) from e
        message = 'Failed to acquire lock {!r} because {}.'.format(lock_id, e)
        raise LockSocketExistsError(message) from e


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


def run_bot():
    bot = Bot()
    bot.run()


def run_bot_with_lock_socket():
    logging.info('Trying to acquire socket lock.')
    try:
        create_lock_socket()
    except CannotCreateLockSocketError as e:
        logging.warning(e)
        should_exit = False
    except LockSocketExistsError as e:
        logging.error(e)
        should_exit = False
    else:
        logging.info('Acquired lock.')
        run_bot()
        should_exit = False
    return should_exit


def run_bot_with_lock_file():
    path = os.path.join(os.path.dirname(__file__), '.timekeeper.pid')
    logging.info('Trying to acquire file lock.')
    try:
        create_lock_file(path)
    except LockFileExistsError as e:
        logging.error(e)
        should_exit = True
    else:
        logging.info('Acquried lock.')
        try:
            run_bot()
        finally:
            remove_lock_file(path)
        should_exit = True
    return should_exit


def main():
    run_bot_with_lock_socket() or run_bot_with_lock_file()


if __name__ == '__main__':
    main()
