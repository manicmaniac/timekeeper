from datetime import datetime, timedelta

from peewee import (BooleanField, CharField, CompositeKey, DateTimeField,
                    ForeignKeyField, IntegerField, Model, MySQLDatabase,
                    SqliteDatabase)
import pytz
from slackbot import settings

from timekeeper.database import get_db
from timekeeper.utils import format_timedelta


class BaseModel(Model):
    class Meta:
        database = get_db()

    created_at = DateTimeField(default=datetime.utcnow)  # read/write as UTC


class User(BaseModel):
    id = CharField(primary_key=True)
    name = CharField(null=True, unique=True)
    timezone_id = CharField(null=False,
                            default=settings.TIMEKEEPER_DEFAULT_TIMEZONE)
    trackable = BooleanField(default=False)

    def last_attendance(self):
        """
        Returns the last attendance of the user.

        :return: the last created Attendance object if it exists else None
        """
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


class DailyAttendance(Attendance):
    class Meta:
        primary_key = CompositeKey('date', 'user_id')

    break_count = IntegerField(null=False)
    working_time_seconds = IntegerField(null=False)
    user = ForeignKeyField(User, null=False, related_name='daily_attendances',
                           on_delete='CASCADE')

    create_view_statement_mysql = """\
            create or replace view dailyattendance as
            select min(started_at)
                as started_at,
                    max(finished_at)
                as finished_at,
                    count(*) - 1
                as break_count,
                    sum(unix_timestamp(finished_at) - unix_timestamp(started_at))
                as working_time_seconds,
                    min(created_at)
                as created_at,
                    user_id
                from attendance
            where started_at is not null
                and finished_at is not null
            group by date(started_at), user_id
            order by started_at"""

    create_view_statement_sqlite = """\
            create view if not exists dailyattendance as
            select min(started_at)
                as started_at,
                    max(finished_at)
                as finished_at,
                    count(*) - 1
                as break_count,
                    sum(cast(strftime('%s', finished_at)
                            as integer)
                        - cast(strftime('%s', started_at)
                                as integer))
                as working_time_seconds,
                    min(created_at)
                as created_at,
                    user_id
                from attendance
            where started_at is not null
                and finished_at is not null
            group by date(started_at), user_id
            order by started_at"""

    @classmethod
    def create_view(cls):
        if isinstance(cls._meta.database, MySQLDatabase):
            statement = cls.create_view_statement_mysql
        elif isinstance(cls._meta.database, SqliteDatabase):
            statement = cls.create_view_statement_sqlite
        else:
            raise NotImplementedError('An SQL statement for the current database {} is not implemented.'.format(cls._meta.database))
        cls._meta.database.execute_sql(statement)

    @property
    def working_time(self):
        return timedelta(seconds=self.working_time_seconds)
