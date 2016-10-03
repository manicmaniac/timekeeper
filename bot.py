import logging
import socket

from slackbot.bot import Bot

lock_socket = None


def is_lock_free():
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    lock_id = 'timekeeper-slackbot'
    try:
        lock_socket.bind('\0' + lock_id)
    except socket.error:
        logging.info('Failed to acquire lock {!r}'.format(lock_id))
        return False
    else:
        logging.debug('Acquired lock {!r}'.format(lock_id))
        return True


def main():
    if is_lock_free():
        bot = Bot()
        bot.run()


if __name__ == '__main__':
    main()
