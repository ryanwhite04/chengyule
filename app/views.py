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
from app.models import User
from requests import get
app = Blueprint("", __name__)

def getPuzzle(chengyu):
    print(chengyu)
    options = sorted(list(u"".join([c["chinese"] for c in chengyu])))
    return {
        # "options": [(translate(option), option) for option in options],
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
    print(count, key)
    return getPuzzle(select('static/chengyu.json', count or 4, bytes(key or 1)))

@app.route("/")
@app.route("/index")
def daily():
    key = bytes(int(time())//(60*60*24))
    return render_template('index.html',
        title="Daily Puzzle",
        puzzle=getPuzzle(select('static/chengyu.json', 4, key)),
        highlight=True,
    )

@app.route("/random")
def random():
    return render_template('index.html',
        title="Random Puzzle",
        puzzle=getPuzzle(select('static/chengyu.json', 4)),
        highlight=True,
    )

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