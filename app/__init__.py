from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
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
    if app.config["ENV"] == "development":
        # from pprint import pprint
        # pprint(app.config)
        with app.app_context():
            db.create_all()
    return app