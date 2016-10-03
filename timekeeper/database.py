from playhouse.db_url import connect
from slackbot import settings

db = connect(settings.TIMEKEEPER_DATABASE_URI)
