def format_timedelta(timedelta):
    total_minutes, seconds = divmod(timedelta.seconds, 60)
    hours, minutes = divmod(total_minutes, 60)
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)


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
