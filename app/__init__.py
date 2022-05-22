from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_language import Language
from config import Config
from app.commands import Cli

# Create Services for export
db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()
language = Language()
cli = Cli()

def create_app(config=Config):

    app = Flask(__name__,
        static_folder="../static",
        template_folder="../templates"
    )

    app.config.from_object(config())

    for key in app.config["SHOW"]:
        print(key, app.config[key])

    # Register services
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    language.init_app(app)
    login.login_view = "login"
    cli.init_app(app, db)

    from app.converters import ChineseListConverter
    app.url_map.converters["zh_list"] = ChineseListConverter
    from app.views import app as views
    app.register_blueprint(views)

    return app
