from sqlalchemy.exc import (
    ProgrammingError,
    OperationalError,
    IntegrityError,
)
from sys import stdin, stdout, stderr
from json import loads, dumps
from requests import post
from click import argument, File, pass_context

class Cli:

    def init_app(self, app, db):
        from app.models import Code, Text
        @app.cli.group()
        @pass_context
        def languages(context):
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