from peewee import OperationalError, SqliteDatabase
from playhouse.db_url import connect
from playhouse.migrate import SqliteMigrator, migrate
from slackbot import settings

_db = None


def get_db():
    global _db
    if _db is None:
        _db = connect(settings.TIMEKEEPER_DATABASE_URI)
    return _db


def migrate_db():
    db = get_db()
    if isinstance(db, SqliteDatabase):
        from timekeeper.models import User
        migrator = SqliteMigrator(db)
        try:
            with db.transaction():
                migrate(migrator.add_column('user', 'name', User.name))
        except OperationalError as e:
            message, *_ = e.args
            if 'duplicate column name: name' not in message:
                raise
