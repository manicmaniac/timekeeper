from peewee import OperationalError
from playhouse.db_url import connect
from playhouse.migrate import SqliteMigrator, migrate
from slackbot import settings

db = connect(settings.TIMEKEEPER_DATABASE_URI)


def migrate_db():
    from timekeeper.models import User
    migrator = SqliteMigrator(db)
    try:
        with db.transaction():
            migrate(migrator.add_column('user', 'name', User.name))
    except OperationalError as e:
        message, *_ = e.args
        if 'duplicate column name: name' not in message:
            raise
