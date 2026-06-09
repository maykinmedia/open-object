import os

from maykin_common.config import config

os.environ.setdefault("DB_USER", config("DB_USER", default="objects"))
os.environ.setdefault("DB_NAME", config("DB_NAME", default="objects"))
os.environ.setdefault("DB_PASSWORD", config("DB_PASSWORD", default="objects"))
os.environ.setdefault("DB_HOST", config("DB_HOST", default="db"))
os.environ.setdefault("DB_CONN_MAX_AGE", "60")

os.environ.setdefault("ENVIRONMENT", "docker")
os.environ.setdefault("LOG_STDOUT", "yes")
os.environ.setdefault("LOG_FORMAT_CONSOLE", "json")

from .production import *  # noqa isort:skip
