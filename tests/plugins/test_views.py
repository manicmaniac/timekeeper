from textwrap import dedent
import unittest
from unittest.mock import ANY, MagicMock, patch, sentinel

from timekeeper.plugins.views import (render_timesheet, render_daily_timesheet,
                                      render_contribution_figure)


class TestViews(unittest.TestCase):
    def test_render_timesheet(self):
        expected_value = dedent("""\
            start                finish               working time
            -------------------  -------------------  --------------
            2017-01-01 00:00:00  2017-01-01 03:00:00  03:00:00
            2017-01-02 00:00:00  2017-01-02 03:00:00  03:00:00""")
        attendances = MagicMock(__iter__=lambda self: iter([
            MagicMock(started_at_display='2017-01-01 00:00:00',
                      finished_at_display='2017-01-01 03:00:00',
                      working_time_display='03:00:00'),
            MagicMock(started_at_display='2017-01-02 00:00:00',
                      finished_at_display='2017-01-02 03:00:00',
                      working_time_display='03:00:00'),
        ]))
        self.assertEqual(render_timesheet(attendances), expected_value)

    def test_render_daily_timesheet(self):
        self.maxDiff = None
        expected_value = dedent("""\
            start                finish                 break count  working time
            -------------------  -------------------  -------------  --------------
            2017-01-01 00:00:00  2017-01-01 03:00:00              0  03:00:00
            2017-01-02 00:00:00  2017-01-02 03:00:00              1  03:00:00""")
        daily_attendances = MagicMock(__iter__=lambda self: iter([
            MagicMock(started_at_display='2017-01-01 00:00:00',
                      finished_at_display='2017-01-01 03:00:00',
                      break_count=0,
                      working_time_display='03:00:00'),
            MagicMock(started_at_display='2017-01-02 00:00:00',
                      finished_at_display='2017-01-02 03:00:00',
                      break_count=1,
                      working_time_display='03:00:00'),
        ]))
        self.assertEqual(render_daily_timesheet(daily_attendances), expected_value)

    def test_render_contribution_figure(self):
        series = sentinel.some_object
        with patch('matplotlib.pyplot.figure') as figure, patch('calmap.yearplot') as yearplot:
            render_contribution_figure(series)
            figure.assert_called_once_with(figsize=(8, 2), dpi=72)
            figure().add_axes.assert_called_once_with([0, 0, 1, 1])
            yearplot.assert_called_once_with(series, ax=ANY)
