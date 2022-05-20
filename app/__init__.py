from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_language import Language
from config import Config
from app.converters import ChineseListConverter
db = SQLAlchemy()
login = LoginManager()
login.login_view = "login"
migrate = Migrate()
language = Language()
def create_app(config=Config):
    app = Flask(__name__,
        static_folder="../static",
        template_folder="../templates"
    )
    app.url_map.converters["zh_list"] = ChineseListConverter
    app.config.from_object(config)
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    language.init_app(app)
    from app.views import app as views
    app.register_blueprint(views)
    from app.commands import register
    register(app, db)
    return app