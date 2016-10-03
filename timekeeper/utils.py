def format_timedelta(timedelta):
    total_minutes, seconds = divmod(timedelta.seconds, 60)
    hours, minutes = divmod(total_minutes, 60)
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)
