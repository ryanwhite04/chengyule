from app.chengyu import select
from werkzeug.security import generate_password_hash
from time import time
from json import loads
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.forms import Registration, Login
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user
from app import db
from app.models import User
app = Blueprint("", __name__)

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