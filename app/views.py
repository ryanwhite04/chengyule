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
)
from json import dumps
from app.forms import Registration, Login
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_user, logout_user
from app import db, language
from flask_language import current_language
from app.models import User, Game, Code, Note, Text
from requests import get
from random import randint
app = Blueprint("", __name__)

@app.app_context_processor
def inject_language():
    current = str(current_language)
    key = current_app.config["TRANSLATION_KEY"]
    def get_languages():
        allowed = Code.query.all()
        names = translate(
            [code.text for code in allowed],
            key,
            current,
        )
        return [
            (code.id, names[index])
            for index, code
            in enumerate(allowed)
        ]
    def translateWord(word):
        return translate([word], key, current)[0]
    return dict(
        current_language=str(current_language),
        _=translateWord,
        get_languages=get_languages,
    )

@language.allowed_languages
def get_allowed_languages():
    return [code.id for code in Code.query.all()]

@language.default_language
def get_default_language():
    return "en"

@app.route('/language', methods=["POST"])
def set_language():
    language.change_language(request.form.get("language"))
    return redirect(request.referrer)

@app.route("/game/<int:id>", methods=["GET", "POST"])
def game(id, title=None, words=4):
    puzzle = getPuzzle(select('static/chengyu.json', id, words))
    game = Game.query.get(id) or Game(id=id, word=puzzle["answer"])
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
        options=puzzle["options"],
        question=puzzle["question"],
    )

def getPuzzle(chengyu):
    options = sorted(list(u"".join([c["chinese"] for c in chengyu])))
    return {
        "options": options,
        "answer": chengyu[0]["chinese"],
        "question": chengyu[0]["english"]
    }

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

@app.route("/translation/<zh_list:words>")
def translation(words):
    key = current_app.config["TRANSLATION_KEY"]
    language = str(current_language)
    translations = translate(words, key, language)
    return Response(
        dumps(translations),
        mimetype="application/json",
    )

@app.route("/chengyu/<int:count>/<int:key>")
def chengyu(count, key):
    return getPuzzle(select('static/chengyu.json', key or 1, count or 4))

@app.route("/")
@app.route("/index")
def daily():
    id = int(time())//(60*60*24) # Today in binary
    return game(id, "Daily Puzzle")

@app.route("/random")
def random():
    id = randint(0, 0xFFFFFFFF) # random big number
    return game(id, "Random Puzzle")

@app.route("/history")
def history():
    with open("history.json") as file: games = loads(file.read())
    return render_template("history.html", games=games, hightlight=True)

@app.route("/registration", methods=['GET', 'POST'])
def register():
    form = Registration()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data))
            db.session.add(user)
            try:
                db.session.commit()
                login_user(user, remember=True) # TODO make this optional
                return redirect(url_for('daily'))
            except IntegrityError as error:
                flash(error, 'error')
                return render_template(
                    'register.html',
                    form=form,
                    title="Registration Page",
                )
    else: return render_template('register.html', form=form, title="Registration Page")

@app.route('/table')
def tables():
    if current_app.config["ENV"] == "development":
        return render_template(
            "tables.html",
            tables=db.metadata.tables.keys(),
            title="Tables"
        )
    return "No"

@app.route('/table/<table>')
def table(table):
    if current_app.config["ENV"] == "development":
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
    return "No"

@app.route('/user')
def user():
    if current_user.is_authenticated:
        return current_user.username
    else:
        return "Not logged in"

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