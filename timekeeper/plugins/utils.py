from contextlib import contextmanager
from shutil import rmtree
from tempfile import mkdtemp


@contextmanager
def create_temp_dir():
    path = mkdtemp()
    try:
        yield path
    finally:
        rmtree(path)


def is_direct_message(channel_id):
    return channel_id.startswith('D')


def safe_upload_file(message, filename, path, comment, is_text_file=False):
    channel_id = message.body['channel']
    if not is_direct_message(channel_id):
        return message.channel.upload_file(filename, path, comment)
    if not is_text_file:
        return message.reply(
            'Sorry, I cannot upload a file in the private channel.'
        )
    with open(path) as f:
        text = f.read()
        message.reply(triple_backquoted(text))


def triple_backquoted(text):
    return '```\n' + text + '\n```'
