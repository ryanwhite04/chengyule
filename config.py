from dotenv import load_dotenv
from os.path import abspath, dirname, join
from os import environ

load_dotenv(join(abspath(dirname(__file__)), ".env"))
def database_URL():
    url = environ.get("DATABASE_URL") or "sqlite:///../app.db"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://")
    return url

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = database_URL()
    SECRET_KEY = environ.get("SECRET_KEY") or "SECRET_KEY"
    TRANSLATION_KEY = environ.get("TRANSLATION_KEY") or "TRANSLATION_KEY"

print(Config)