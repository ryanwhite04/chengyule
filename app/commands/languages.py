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

    def __init__(self):

        def update(output, key):
            json = post("https://translation.googleapis.com/language/translate/v2/languages", {
                "target": "zh",
                "key": key,
            }).json()
            try:
                languages = json["data"]["languages"]
                data = {
                    item["language"]: item["name"]
                    for item in languages
                }
                if output == "-": output = 1 # set to stdout
                with open(output, "w") as file:
                    file.write(dumps(
                        data,
                        indent=4,
                        sort_keys=True,
                        ensure_ascii=False,
                    ))
            except KeyError:
                data = json["error"]["message"]
                stderr.write(data)
            except: raise
        
        def list(Code):
            try:
                return [code for code in Code.query.where(Code.allowed).all()]
            except (ProgrammingError, OperationalError) as e:
                print("""
                    Code table not in database,
                    Try updating database first with 
                    >>>flask db upgrade
                """)
            except: raise
        
        def upgrade(db, Text, Code):
            available = loads(open("languages/index.json").read())
            settings = open("languages/allowed")
            default = settings.readline()
            allowed = settings.readlines()
            allowed.append(default)
            try:
                for code, name in available.items():
                    try:
                        db.session.add(Text(name))
                        db.session.flush()
                        db.session.add(Code(code, name))
                        db.session.commit()
                    except IntegrityError as e:
                        db.session.rollback()
                        # print(f"{name}, {name} is already installed", file=stderr)
            except (ProgrammingError, OperationalError) as e:
                print("""
                    Code table not in database,
                    Try updating database first with 
                    >>>flask db upgrade
                """)
            except: raise

        def install(db, Code):
            file = open("languages/allowed")
            default = file.readline()
            allowed = file.readlines()
            allowed.append(default)

            # Reset
            for code in Code.query.where(Code.allowed).all():
                code.allowed = False
                code.default = False
            
            # Set
            for code in allowed:
                try:
                    c = Code.query.get(code.strip())
                    c.allowed = True
                    if code == default: c.default = True
                    db.session.add(c)
                    db.session.commit()
                except IntegrityError as e:
                    db.session.rollback()
                    print(f"{code} is not available", file=stderr)
                except: raise

        def add(path, code):
            codes = [line.strip() for line in open(path).readlines()]
            with open(path, "w") as file:
                if not code in codes:
                    codes.append(code)
                file.write(u"\n".join(codes))

        def remove(path, code):
            codes = [line.strip() for line in open(path).readlines()]
            if codes[0] == code:
                print("That is the default, change default first", file=stderr)
            elif code in codes:
                codes.remove(code)
                with open(path, "w") as file:
                    file.write(u"\n".join(codes))

        def default(path, code):
            codes = [line.strip() for line in open(path).readlines()]
            if codes[0] == code:
                return
            else:
                if code in codes: codes.remove(code)
                codes.insert(0, code)
                with open(path, "w") as file:
                    file.write(u"\n".join(codes))

        def translate(language, Text, Note, db):
            translations = {}
            try:
                translations =  loads(open(f"languages/{language}.json").read())
            except FileNotFoundError:
                pass
            for key, value in translations.items():
                try:
                    text = Text.query.get(key) or Text(key)
                    note = Note.query.get({
                        "text": key,
                        "code": language,
                    }) or Note(value, language, key)
                    note.content = value
                    note.verified = True
                    db.session.add(text)
                    db.session.add(note)
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise

        self.update = update
        self.upgrade = upgrade
        self.list = list
        self.install = install
        self.add = add
        self.remove = remove
        self.default = default
        self.translate = translate

    def init_app(self, app, db):
        from app.models import Code, Text, Note
        @app.cli.group()
        @pass_context
        def languages(context):
            """Translation and localization commands"""
            pass

        @languages.command()
        @argument("output", default="languages/index.json")
        def update(output):
            """
            Update list of available languages
            Saved to OUTPUT
            Example:
            >>>flask languages update languages.json
            """
            self.update(output, app.config["TRANSLATION_KEY"])

        @languages.command()
        def list():
            """
            List installed languages
            These locales are in the database and will offer a menu option to clients
            These are the languages with "allowed" set to true
            """
            for code in self.list(Code):
                print(code)

        @languages.command()
        def upgrade():
            """
            Upload all available languages to database
            This should be run after an update, or to initialise languages
            These languages won't be set to "allowed"
            """
            self.upgrade(db, Text, Code)
            self.install(db, Code)
            for code in self.list(Code):
                self.translate(code.id, Text, Note, db)
        
        @languages.command()
        def install():
            """
            Install a new language from INPUT
            Saves the language into the database
            """
            self.install(db, Code)

        @languages.command()
        @argument("language")
        def add(language):
            """
            Add a language to allowed languages
            Update database with installed languages
            """
            self.add("languages/allowed", language)
            self.install(db, Code)

        @languages.command()
        @argument("language")
        def remove(language):
            """
            Remove a language from allowed list
            Can't remove default language
            Must set new default first
            Update database with installed languages
            """
            self.remove("languages/allowed", language)
            self.install(db, Code)

        @languages.command()
        @argument("language")
        def default(language):
            """
            Set the default language
            Will be added if not currently allowed
            Update database with installed languages
            """
            self.default("languages/allowed", language)
            self.install(db, Code)

        @languages.command()
        @argument("language", default=None)
        def translate(language):
            """
            Upload all translations in the given language
            Uploadd all if no language given
            """
            self.translate(language, Text, Note, db)