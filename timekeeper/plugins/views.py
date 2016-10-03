import matplotlib
matplotlib.use('Agg')  # noqa

import calmap
import matplotlib.pyplot as plt

from tabulate import tabulate


def render_timesheet(attendances):
    table = map(_render_timesheet_entry, attendances)
    headers = ['start', 'finish', 'working time']
    return tabulate(table, headers=headers)


def render_daily_timesheet(daily_attendances):
    table = map(_render_daily_timesheet_entry, daily_attendances)
    headers = ['start', 'finish', 'break count', 'working time']
    return tabulate(table, headers=headers)


def render_contribution_figure(series):
    fig = plt.figure(figsize=(8, 2), dpi=72)
    ax = fig.add_axes([0, 0, 1, 1])
    ax = calmap.yearplot(series, ax=ax)
    return fig


def _render_timesheet_entry(attendance):
    a = attendance
    return (a.started_at_display,
            a.finished_at_display,
            a.working_time_display)


def _render_daily_timesheet_entry(daily_attendance):
    d = daily_attendance
    return (d.started_at_display,
            d.finished_at_display,
            d.break_count,
            d.working_time_display)
