"""
I'm a bot to track your working time.
If you want me to track your daily workload,
please say `@timekeeper track me`.

I can understand the following words and something like them;

`started working`
`continue working`
`finished working`
`stopped working`
`@timekeeper contributions`
`@timekeeper help`
`@timekeeper timesheet`
`@timekeeper track me`
`@timekeeper do not track me`
`@timekeeper set my timezone as Europe/London`

Again, I won't track you until you say `@timekeeper track me`!
"""

from datetime import datetime
import re
import os
from textwrap import dedent

import pytz
from slackbot import settings
from slackbot.bot import respond_to, listen_to
from slackbot.utils import create_tmp_file

from timekeeper.database import get_db, migrate_db
from timekeeper.models import Attendance, DailyAttendance, User
from timekeeper.plugins.decorators import with_user
from timekeeper.plugins.utils import create_temp_dir, safe_upload_file
from timekeeper.plugins.views import (render_contribution_figure,
                                      render_daily_timesheet,
                                      render_timesheet)
from timekeeper.stats import working_time_ratio_series


def on_start_listening():
    db = get_db()
    db.connect()
    db.create_tables([User, Attendance], safe=True)
    DailyAttendance.create_view()
    migrate_db()


on_start_listening()


@listen_to('作業を開始します')
@listen_to('(作業を)?再開します')
@listen_to('start(ed)? working', re.IGNORECASE)
@listen_to('continued? working', re.IGNORECASE)
@listen_to('resumed? working', re.IGNORECASE)
@with_user
def on_start_working(message, user, *args):
    if not user.trackable:
        return
    last_attendance = user.last_attendance()
    has_unfinished_work = last_attendance and not last_attendance.finished_at
    attendance = Attendance.create(started_at=datetime.utcnow(), user=user)
    attendance.save()
    message.react('stopwatch')
    if has_unfinished_work:
        message.reply(dedent("""\
            I think you missed to inform finishing the last one.
            However I'll record you start your work now."""))


@listen_to('作業を終了します')
@listen_to('(作業を)?中断します')
@listen_to('finish(ed)? working', re.IGNORECASE)
@listen_to('report working', re.IGNORECASE)
@listen_to('stop(ped)? working', re.IGNORECASE)
@with_user
def on_finish_working(message, user, *args):
    if not user.trackable:
        return
    attendance = user.last_attendance()
    if not attendance or attendance.finished_at:
        attendance = Attendance.create(user=user)
    attendance.finished_at = datetime.utcnow()
    has_unstarted_work = not attendance.started_at and attendance.finished_at
    attendance.save()
    message.react('stopwatch')
    if has_unstarted_work:
        message.reply(dedent("""\
            I think you missed to inform starting this work.
            However I'll record you finish your work now."""))


@respond_to('^introduce yourself$', re.IGNORECASE)
@respond_to('^help$')
def help(message):
    message.reply(__doc__)


@respond_to('^track me$', re.IGNORECASE)
@with_user
def set_trackable(message, user):
    if user.trackable:
        return message.reply("I'm already tracking you.")
    user.trackable = True
    user.save()
    message.reply('OK, I will track you.')


@respond_to('^do not track me$', re.IGNORECASE)
@respond_to("^don'?t track me$", re.IGNORECASE)
@with_user
def set_untrackable(message, user):
    if not user.trackable:
        return message.reply("I didn't track you.")
    user.trackable = False
    user.save()
    message.reply("OK, I won't track you any more.")


@respond_to('set my time ?zone as (.*)$', re.IGNORECASE)
@respond_to('my time ?zone is (.*)$', re.IGNORECASE)
@with_user
def set_timezone(message, user, timezone_id):
    try:
        user.timezone = pytz.timezone(timezone_id)
    except pytz.UnknownTimeZoneError:
        message.reply("Sorry but I can't recognize it. Maybe a typo?")
    else:
        user.save()
        message.reply('OK, I updated your timezone.')


@respond_to('^(show )?(m[ey] )?timesheet$')
@with_user
def show_timesheet(message, user, *args):
    attendances = user.attendances.order_by(Attendance.started_at.desc()).limit(30)
    if not attendances:
        return message.reply("Sorry but I don't have your timesheet.")
    timesheet = render_timesheet(attendances)
    filename = 'timesheet.md'
    with create_tmp_file(bytes(timesheet, 'utf-8')) as path:
        safe_upload_file(message, filename, path, 'Here is your timesheet.',
                         is_text_file=True)


@respond_to('^(show )?(m[ey] )?daily timesheet$')
@respond_to('^(show )?(m[ey] )?timesheet by day$')
@with_user
def show_daily_timesheet(message, user, *args):
    daily_attendances = user.daily_attendances.order_by(DailyAttendance.started_at.desc()).limit(30)
    if not daily_attendances:
        return message.reply("Sorry but I don't have your daily timesheet.")
    daily_timesheet = render_daily_timesheet(daily_attendances)
    filename = 'daily_timesheet.md'
    with create_tmp_file(bytes(daily_timesheet, 'utf-8')) as path:
        safe_upload_file(message, filename, path,
                         'Here is your daily timesheet.', is_text_file=True)


@respond_to('contributions')
@with_user
def show_contributions(message, user):
    if not user.attendances:
        return message.reply("Sorry but I don't have your timesheet.")
    message.reply('OK, wait a moment...')
    series = working_time_ratio_series(user)
    figure = render_contribution_figure(series)
    filename = 'contributions.png'
    with create_temp_dir() as temp_dir:
        path = os.path.join(temp_dir, filename)
        figure.savefig(path)
        safe_upload_file(
            message,
            filename,
            path,
            'Here. Regardless of your timezone, each days are plotted in UTC.'
        )


@respond_to('^debug (.*)$')
def debug(message, script):
    is_debug = os.getenv('TIMEKEEPER_DEBUG') not in (None, '', '0')
    message.reply(repr(eval(script)) if is_debug else settings.DEFAULT_REPLY)


@respond_to('quine')
def quine(message):
    with open(__file__, 'r') as f:
        safe_upload_file(message, f.name, f.name, '', is_text_file=True)
