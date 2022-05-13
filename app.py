from flask import Flask, render_template, redirect, url_for
from chengyu import select
from os import listdir, environ
from time import time
from requests import get
from json import loads
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from Registration import Registration

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a259223f6fbaa6b4678936fa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
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
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('daily'))
    return render_template('register.html', form=form, title="Registration Page")
