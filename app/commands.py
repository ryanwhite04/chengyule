from requests import post
from app.models import Text, Code, User
from json import loads, dumps
from click import argument, option, File
from sys import stdin, stdout, stderr
from sqlalchemy.exc import (
    ProgrammingError,
    OperationalError,
    IntegrityError,
)

def register(app, db):

    @app.cli.group()
    def admin():
        """User Management"""
        pass

    @admin.command()
    @argument("username")
    @option("--role", "-r", default=None, show_default=True)
    def update(username, role):
        """
        Update users
        Roles:
            0: admin (has access to database)
        """
        roles = ["admin", "editor"]
        user = User.query.where(User.username == username).first()
        try:
            user.role = roles[int(role)] if role else None
            db.session.add(user)
            db.session.commit()
        except IndexError as e:
            print("That role doesn't exist")
            print(f"Roles include:")
            for i, role in enumerate(roles):
                print(f"{i}: {role}")
            db.session.rollback()
        print(User.query.get(user.id))

    @app.cli.group()
    def languages():
        """Translation and localization commands"""
        pass

    @languages.command()
    @argument("output", type=File("w", "UTF8"))
    def update(output):
        """
        Update list of available languages
        Saved to OUTPUT
        Example:
        >>>flask languages update languages.json
        """
        json = post("https://translation.googleapis.com/language/translate/v2/languages", {
            "target": "zh",
            "key": app.config["TRANSLATION_KEY"],
        }).json()
        try:
            languages = json["data"]["languages"]
            data = {
                item["language"]: item["name"]
                for item in languages
            }
        except KeyError:
            data = json["error"]["message"]
        except: raise
        output.write(dumps(
            data,
            indent=4,
            sort_keys=True,
            ensure_ascii=False,
        ))


    @languages.command()
    def list():
        """
        List installed languages
        These locales are in the database and will offer a menu option to clients
        """
        try:
            [print(code) for code in Code.query.all()]
        except (ProgrammingError, OperationalError) as e:
            print("""
                Code table not in database,
                Try updating database first with 
                >>>flask db upgrade
            """)
        except: raise

    @languages.command()
    @argument("input", type=File("r", "UTF8"))
    @argument("language")
    def install(input, language="zh"):
        """
        Install a new language from INPUT
        Saves the language into the database
        """
        print()
        try:
            languages = loads(input.read())
            name = languages[language]
            db.session.add(Text(name))
            db.session.flush()
            db.session.add((Code(language, name)))
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print(f"{name}, {language} is already installed", file=stderr)
        except: raise
        print("Currently Installed:")
        for code in Code.query.all():
            print(f"{code.id}:{code.text}")


