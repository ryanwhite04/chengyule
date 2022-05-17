from requests import post
from app.models import Text, Code
from json import loads, dumps
from click import argument, File
from sys import stdin, stdout, stderr
from sqlalchemy.exc import (
    ProgrammingError,
    OperationalError,
    IntegrityError,
)

def register(app, db):

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
        try:
            languages = loads(input.read())
            name = languages[language]
            text = Text(name)
            code = Code(language, name)
            db.session.add_all((text, code))
            db.session.commit()
            print(f"{name}, {language} installed", file=stdout)
        except IntegrityError as e:
            print(f"{name}, {language} already installed", file=stderr)
        except: raise


