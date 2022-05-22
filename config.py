from dotenv import load_dotenv
from os.path import abspath, dirname, join
from os import environ
from json import loads

load_dotenv(join(abspath(dirname(__file__)), ".env"))
# This is a list of environment variables to display to developers
SHOW = environ.get("SHOW")

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        environ.get("DATABASE_URL") or ""
    ).replace("postgres://", "postgresql://")
    SECRET_KEY = environ.get("SECRET_KEY")
    TRANSLATION_KEY = environ.get("TRANSLATION_KEY")
    SHOW = loads(SHOW) if SHOW else []