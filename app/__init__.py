from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user
from config import Config
db = SQLAlchemy()
login = LoginManager()

def create_app(config=Config):
    app = Flask(__name__,
        static_folder="../static",
        template_folder="../templates"
    )
    app.config.from_object(config)
    db.init_app(app)
    login.init_app(app)
    from app.views import app as views
    app.register_blueprint(views)
    return app

from app.models import User, Game, Play
