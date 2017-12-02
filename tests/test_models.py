from datetime import datetime, timedelta, tzinfo
import unittest
from unittest.mock import patch

from peewee import SqliteDatabase
from pytz import timezone

from timekeeper.models import Attendance, DailyAttendance, User


class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = SqliteDatabase(':memory:')
        cls.database.set_autocommit(False)
        cls.patchers = []
        cls.patchers.append(patch.object(User._meta, 'database', cls.database))
        cls.patchers.append(patch.object(Attendance._meta, 'database', cls.database))
        for patcher in cls.patchers:
            patcher.start()
        cls.database.connect()
        cls.database.create_tables([Attendance, User], safe=True)

    @classmethod
    def tearDownClass(cls):
        for patcher in cls.patchers:
            patcher.stop()
        cls.database.close()

    def setUp(self):
        self.database.begin()
        self.user = User.create(id='id', name='name', timezone_id='Asia/Tokyo')

    def tearDown(self):
        self.database.rollback()

    def test_last_attendance_returns_none_without_attendances(self):
        """last_attendance() returns None when the user has no attendance."""
        self.assertIsNone(self.user.last_attendance())

    def test_last_attendance_returns_attendance(self):
        """
        last_attendance() returns the last created Attendance object
        when the user has multiple attendances.
        """
        started_and_finished_datetimes = [
            (datetime(2017, 1, 1), datetime(2017, 1, 2)),
            (datetime(2017, 1, 2), datetime(2017, 1, 3)),
            (datetime(2017, 1, 3), datetime(2017, 1, 4)),
        ]
        for started_at, finished_at in started_and_finished_datetimes:
            attendance = Attendance.create(started_at=started_at, finished_at=finished_at, user=self.user)
        self.assertEqual(self.user.last_attendance(), attendance)

    def test_timezone_returns_timezone_object(self):
        self.assertIsInstance(self.user.timezone, tzinfo)
        dt = datetime(2017, 1, 1)
        self.assertEqual(self.user.timezone.tzname(dt), 'JST')

    def test_set_timezone_changes_timezone_id(self):
        self.assertEqual(self.user.timezone_id, 'Asia/Tokyo')
        self.user.timezone = timezone('US/Eastern')
        self.assertEqual(self.user.timezone_id, 'US/Eastern')


class TestAttendance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = SqliteDatabase(':memory:')
        cls.database.set_autocommit(False)
        cls.patchers = []
        cls.patchers.append(patch.object(User._meta, 'database', cls.database))
        cls.patchers.append(patch.object(Attendance._meta, 'database', cls.database))
        for patcher in cls.patchers:
            patcher.start()
        cls.database.connect()
        cls.database.create_tables([Attendance, User], safe=True)

    @classmethod
    def tearDownClass(cls):
        for patcher in cls.patchers:
            patcher.stop()
        cls.database.close()

    def setUp(self):
        self.database.begin()
        self.user = User.create(id='id', name='name', timezone_id='Asia/Tokyo')

    def tearDown(self):
        self.database.rollback()

    def test_is_complete_parameterized(self):
        # (started_at, finished_at, expected_value)
        parameters = [
            (None, None, False),
            (datetime(2017, 1, 1), None, False),
            (None, datetime(2017, 1, 2), False),
            (datetime(2017, 1, 1), datetime(2017, 1, 2), True),
        ]
        for started_at, finished_at, expected_value in parameters:
            attendance = Attendance.create(started_at=started_at,
                                           finished_at=finished_at,
                                           user=self.user)
            self.assertEqual(attendance.is_complete, expected_value)

    def test_working_time_parameterized(self):
        # (started_at, finished_at, expected_value)
        parameters = [
            (None, None, None),
            (datetime(2017, 1, 1), None, None),
            (None, datetime(2017, 1, 2), None),
            (datetime(2017, 1, 1), datetime(2017, 1, 2), timedelta(days=1)),
        ]
        for started_at, finished_at, expected_value in parameters:
            attendance = Attendance.create(started_at=started_at,
                                           finished_at=finished_at,
                                           user=self.user)
            self.assertEqual(attendance.working_time, expected_value)

    def test_started_at_display(self):
        started_at = datetime(2017, 1, 1)
        attendance = Attendance.create(started_at=started_at, user=self.user)
        self.assertEqual(attendance.started_at_display, '2017-01-01 09:00:00')

    def test_finished_at_display(self):
        finished_at = datetime(2017, 1, 1)
        attendance = Attendance.create(finished_at=finished_at, user=self.user)
        self.assertEqual(attendance.finished_at_display, '2017-01-01 09:00:00')

    def test_working_time_display_parameterized(self):
        # (started_at, finished_at, expected_value)
        parameters = [
            (None, None, None),
            (datetime(2017, 1, 1), None, None),
            (None, datetime(2017, 1, 2), None),
            (datetime(2017, 1, 1), datetime(2017, 1, 1, 12, 34, 56), '12:34:56'),
            (datetime(2017, 1, 1), datetime(2017, 1, 2), '24:00:00'),
            (datetime(2017, 1, 1), datetime(2017, 1, 2, 1), '25:00:00'),
            (datetime(2017, 1, 1), datetime(2017, 1, 3), '48:00:00'),
            (datetime(2017, 1, 1), datetime(2017, 1, 5, 4), '100:00:00'),
        ]
        for started_at, finished_at, expected_value in parameters:
            attendance = Attendance.create(started_at=started_at,
                                           finished_at=finished_at,
                                           user=self.user)
            self.assertEqual(attendance.working_time_display, expected_value)
