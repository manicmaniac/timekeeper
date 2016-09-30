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
from functools import wraps
import re
import os
from shutil import rmtree
from tempfile import mkdtemp

import matplotlib
matplotlib.use('Agg')  # noqa

import calmap as cm
import matplotlib.pyplot as plt
import pandas as pd
from peewee import (BooleanField, CharField, DateTimeField, ForeignKeyField,
                    Model, SqliteDatabase)
import pytz
from slackbot import settings
from slackbot.bot import respond_to, listen_to
from slackbot.utils import create_tmp_file
from tabulate import tabulate

db = SqliteDatabase(settings.TIMEKEEPER_DATABASE)


class BaseModel(Model):
    class Meta:
        database = db

    created_at = DateTimeField(default=datetime.utcnow)  # read/write as UTC


class User(BaseModel):
    id = CharField(primary_key=True)
    timezone_id = CharField(null=False,
                            default=settings.TIMEKEEPER_DEFAULT_TIMEZONE)
    trackable = BooleanField(default=False)

    def last_attendance(self):
        return self.attendances.order_by(Attendance.started_at.desc()).first()

    @property
    def timezone(self):
        return pytz.timezone(self.timezone_id)

    @timezone.setter
    def timezone(self, new_timezone):
        self.timezone_id = new_timezone.zone


class Attendance(BaseModel):
    started_at = DateTimeField(null=True)  # read/write as UTC
    finished_at = DateTimeField(null=True)  # read/write as UTC
    user = ForeignKeyField(User, null=False, related_name='attendances',
                           on_delete='CASCADE')

    @property
    def is_complete(self):
        return bool(self.started_at and self.finished_at)

    @property
    def working_time(self):
        if self.is_complete:
            return self.finished_at - self.started_at

    @property
    def started_at_display(self):
        started_at = self.started_at
        if started_at:
            utc_started_at = pytz.utc.localize(started_at)
            local_started_at = utc_started_at.astimezone(self.user.timezone)
            return local_started_at.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def finished_at_display(self):
        finished_at = self.finished_at
        if finished_at:
            utc_finished_at = pytz.utc.localize(finished_at)
            local_finished_at = utc_finished_at.astimezone(self.user.timezone)
            return local_finished_at.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def working_time_display(self):
        working_time = self.working_time
        if working_time:
            return format_timedelta(working_time)


db.connect()
db.create_tables([User, Attendance], safe=True)


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
        message.reply("""I think you missed to inform finishing the last one.
                         However I'll record you start your work now.""")


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
        message.reply("""I think you missed to inform starting this work.
                         However I'll record you finish your work now.""")


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


@respond_to('timesheet')
@with_user
def show_timesheet(message, user):
    attendances = user.attendances.order_by(Attendance.started_at)
    if not attendances:
        return message.reply("Sorry but I don't have your timesheet.")
    timesheet = render_timesheet(attendances)
    filename = 'timesheet.md'
    with create_tmp_file(bytes(timesheet, 'utf-8')) as path:
        safe_upload_file(message, filename, path, 'Here is your timesheet.',
                         is_text_file=True)


@respond_to('contributions')
@with_user
def show_contributions(message, user):
    if not user.attendances:
        return message.reply("Sorry but I don't have your timesheet.")
    message.reply('OK, wait a moment...')
    tempdir = mkdtemp()
    try:
        filename = 'contributions.png'
        path = os.path.join(tempdir, filename)
        save_contributions_image(path, user)
        safe_upload_file(
            message,
            filename,
            path,
            'Here. Regardless of your timezone, each days are plotted in UTC.'
        )
    finally:
        rmtree(tempdir)


@respond_to('^debug (.*)$')
def debug(message, script):
    is_debug = os.getenv('TIMEKEEPER_DEBUG') not in (None, '', '0')
    message.reply(repr(eval(script)) if is_debug else settings.DEFAULT_REPLY)


@respond_to('quine')
def quine(message):
    with open(__file__, 'r') as f:
        safe_upload_file(message, f.name, f.name, '', is_text_file=True)


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


def is_direct_message(channel_id):
    return channel_id.startswith('D')


def render_timesheet(attendances):
    table = map(render_timesheet_entry, attendances)
    headers = ['start', 'finish', 'working time']
    return tabulate(table, headers=headers)


def render_timesheet_entry(attendance):
    return (attendance.started_at_display,
            attendance.finished_at_display,
            attendance.working_time_display)


def format_timedelta(timedelta):
    total_minutes, seconds = divmod(timedelta.seconds, 60)
    hours, minutes = divmod(total_minutes, 60)
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)


def working_time_ratio_series(user):
    statement = """select date(started_at)
                       as `date`,
                          sum(cast(strftime('%s', finished_at) as integer) -
                              cast(strftime('%s', started_at) as integer))
                       as working_time_seconds
                     from attendance
                    where started_at is not null
                      and finished_at is not null
                      and user_id = ?
                 group by `date`
                 order by `date`;"""
    df = pd.read_sql_query(statement, db.get_conn(), index_col='date',
                           parse_dates=['date'], params=[user.id])
    return df.working_time_seconds / df.working_time_seconds.std()


def save_contributions_image(path, user):
    series = working_time_ratio_series(user)
    fig = plt.figure(figsize=(8, 2), dpi=72)
    ax = fig.add_axes([0, 0, 1, 1])
    ax = cm.yearplot(series, ax=ax)
    ax.figure.savefig(path)
