def format_timedelta(timedelta):
    total_minutes, seconds = divmod(timedelta.total_seconds(), 60)
    hours, minutes = divmod(total_minutes, 60)
    return '{:02.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)
