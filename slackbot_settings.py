import os.path

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
API_TOKEN = os.getenv('SLACK_API_TOKEN')
DEFAULT_REPLY = "Sorry but I didn't understand you. Please say `@timekeeper help` for more information."
ERRORS_TO = os.getenv('TIMEKEEPER_ERRORS_TO')
TIMEKEEPER_DATABASE = os.path.join(BASE_PATH, 'db.sqlite3')
TIMEKEEPER_DEFAULT_TIMEZONE = 'Asia/Tokyo'
PLUGINS = [
    'plugins.timekeeper'
]
