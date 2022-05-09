from flask import Flask, render_template
from chengyu import select
from os import listdir
from time import time
from requests import get
from json import loads
from Registration import Registration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a259223f6fbaa6b4678936fa'

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

@app.route("/registration")
def register():
    form = Registration()
    return render_template('register.html', form=form)
