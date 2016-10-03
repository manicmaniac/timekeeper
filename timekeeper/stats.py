import pandas as pd

from timekeeper.database import db


def working_time_ratio_series(user):
    statement = """select date(started_at) as `date`,
                          working_time_seconds
                     from dailyattendance
                    where user_id = ?"""
    df = pd.read_sql_query(statement, db.get_conn(), index_col='date',
                           parse_dates=['date'], params=[user.id])
    return df.working_time_seconds / df.working_time_seconds.std()
