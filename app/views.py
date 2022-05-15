from app.chengyu import select
from werkzeug.security import generate_password_hash
from time import time
from json import loads
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)
from app.forms import Registration, Login
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_user, logout_user
from app import db
from app.models import User, Game
from requests import get
from random import randint
app = Blueprint("", __name__)

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

@app.route("/translation/<text>")
def translate(text):
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "key": current_app.config["TRANSLATION_KEY"],
        "source": "zh",
        "target": "en",
        "q": text,
    }
    json = get(url, params=params).json()
    try:
        translation = json["data"]["translations"][0]["translatedText"]
        return translation
    except:
        return ""

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