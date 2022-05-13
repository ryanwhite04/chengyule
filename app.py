from flask import Flask, render_template, redirect, url_for, request
from chengyu import select
from werkzeug.security import generate_password_hash
from os import listdir, environ
from time import time
from json import loads
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user
from registration import Registration
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a259223f6fbaa6b4678936fa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login = LoginManager(app)
migrate = Migrate(app, db)
from models import User, Game, Play
def getPuzzle(chengyu):
    return {
        "options": "".join([c["chinese"] for c in chengyu]),
        "answer": chengyu[0]["chinese"],
        "question": chengyu[0]["english"]
    }

@app.route("/chengyu")
def chengyu():
    return getPuzzle(select('static/chengyu.json'))

@app.route("/")
@app.route("/index")
def daily():
    key = bytes(int(time())//(60*60*24))
    return render_template('index.html',
        title="Daily Puzzle",
        puzzle=getPuzzle(select('static/chengyu.json', 4, key))
    )

@app.route("/random")
def random():
    return render_template('index.html',
        title="Random Puzzle",
        puzzle=getPuzzle(select('static/chengyu.json', 4))
    )

@app.route("/history")
def history():
    with open("history.json") as file: games = loads(file.read())
    return render_template("history.html", games=games)

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
                return render_template(
                    'register.html',
                    form=form,
                    title="Registration Page",
                    error=error
                )
    else: return render_template('register.html', form=form, title="Registration Page")

@app.route("/user", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return current_user.email
    return "Not authenticated"