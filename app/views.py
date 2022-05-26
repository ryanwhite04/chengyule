from sqlalchemy import true, and_
from app.chengyu import select
from werkzeug.security import generate_password_hash
from werkzeug.routing import BaseConverter
from time import time
from json import loads, dumps
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
    Response,
    abort,
    escape,
)
from json import dumps
from app.forms import Registration, Login
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_user, logout_user, login_required
from app import db, language
from flask_language import current_language
from app.models import User, Game, Code, Note, Text, Play
from requests import get
from random import randint
app = Blueprint("", __name__)


@app.app_template_filter("_")
def translate_word(word, current=None):
    if not current:
        current = str(current_language)
    key = current_app.config["TRANSLATION_KEY"]
    translated = translate([word], key, current)[0]
    return escape(translated)

@app.app_context_processor
def inject_language():
    return dict(
        current_language=str(current_language),
        get_languages=Code.query.where(Code.allowed).all(),
    )

@language.allowed_languages
def get_allowed_languages():
    return [code.id for code in Code.query.where(Code.allowed).all()]

@language.default_language
def get_default_language():
    return Code.query.where(Code.default).first().id

@app.route('/language', methods=["POST"])
def set_language():
    language.change_language(request.form.get("language"))
    return redirect(request.referrer)

@app.route("/game/<int:id>", methods=["GET", "POST"])
def game(id, title=None, words=4):
    chengyu = select('chengyu.json', id, words)
    game = Game.query.get(id) or Game(id, chengyu)
    if request.method == "POST":
        word = request.form.get("play")
        if current_user.is_authenticated:
            try:
                current_user.play(game, word)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash("Invalid Submission", "error")
        return redirect(url_for("game", id=id))
    title = title or f"Game {id}"
    return render_template('game.html',
        title=title,
        game=game,
        highlight=True,
    )

    

def google_translate(q, target, key, source="zh"):
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "key": key,
        "source": source,
        "target": target,
        "q": q,
    }
    response = get(url, params=params).json()
    # If there was an error, response won't have "data" key
    try:
        translations = [
            translation["translatedText"]
            for translation
            in response["data"]["translations"]
        ]
    except KeyError as e:
        print(response["error"]["message"])
    return translations

def translate(words, key, language):
    if language == "zh": return words
    elif not key:
        return [f"{language}_{word}" for word in words]
    # Find any words not in the cache/database
    missing = set()
    found = {} # { word: translation }
    for word in words:
        if not Text.query.get(word):
            db.session.add(Text(word))
            missing.add(word)
        note = Note.query.get({
            "text": word,
            "code": language,
        })
        if note: found[word] = note.content
        else: missing.add(word)
    db.session.commit()
    # Get missing words from google translate
    if missing:
        missing = list(missing)
        translations = google_translate(
            missing,
            language,
            key,
            "zh"
        )

        # Store any new translations in the cache for next time
        for index, translation in enumerate(translations):
            db.session.add(Note(translation, language, missing[index]))
            found[missing[index]] = translation
        db.session.commit()
    return [found[word] for word in words]

@app.route("/translation/<language>/<zh_list:words>")
def translation(language, words):
    key = current_app.config["TRANSLATION_KEY"]
    translations = translate(words, key, language)
    return Response(
        dumps(translations),
        mimetype="application/json",
    )

@app.route("/")
@app.route("/index")
def daily():
    id = int(time())//(60*60*24) # Today in binary
    return game(id, "Daily Puzzle")

@app.route("/random")
def random():
    return redirect(url_for("game", id=randint(0, 0xFFFFFFFF)))

@app.route("/history")
@login_required
def history():
    return render_template('history.html', Game=Game, User=User, Play=Play)

@app.route("/registration", methods=['GET', 'POST'])
def register():
    # print(request.form.)
    form = Registration()
    if request.method == "POST" and form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data))
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True) # TODO make this optional
            return redirect(url_for('daily'))
        except IntegrityError as error:
            db.session.rollback()
            flash("That username is already registered", 'error')
            return render_template(
                'register.html',
                form=form,
                title="Registration Page",
            )
        except Exception as e:
            print(e)
            raise
    else:
        return render_template('register.html', form=form, title="Registration Page")

@app.errorhandler(404)
def page_note_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def page_forbidden(e):
    return render_template("403.html"), 403

@app.route('/table')
def admin():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return render_template(
                "tables.html",
                tables=db.metadata.tables.keys(),
                title="Tables"
            )
        abort(403)
    return redirect(url_for("login"))

@app.route('/table/<table>')
def table(table):
    if current_user.is_authenticated:
        if current_user.role == "admin":
            Model = next(Model
                for Model
                in db.Model.__subclasses__()
                if Model.__tablename__ == table
            )
            return render_template(
                "table.html",
                columns=db.metadata.tables[table].columns.keys(),
                rows=Model.query.all(),
                title=Model.__name__,
            )
        abort(403)
    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.checkPassword(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('daily'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("daily"))

@app.route('/rules')
def rules():
    return render_template("rules.html")