from dotenv import load_dotenv
from os.path import abspath, dirname, join
from os import environ

load_dotenv(join(abspath(dirname(__file__)), ".env"))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL") or "sqlite:///../app.db"
    SECRET_KEY = environ.get("SECRET_KEY") or "SECRET_KEY"
    TRANSLATION_KEY = environ.get("TRANSLATION_KEY") or "TRANSLATION_KEY"

print(Config)