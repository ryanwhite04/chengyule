from flask import Flask, render_template
from chengyu import select
from os import listdir
from time import time

app = Flask(__name__)

def getPuzzle(chengyu):
    return {
        "options": "".join([c["chinese"] for c in chengyu]),
        "answer": chengyu[0]["chinese"],
        "question": chengyu[0]["english"]
    }

@app.route("/chengyu")
def chegnyu():
    return select()

@app.route("/")
@app.route("/index")
def daily():
    key = bytes(int(time())//(60*60*24))
    chengyu = select('static/chengyu.json', 4, key)
    return render_template('index.html',
        title="Daily Puzzle",
        puzzles=[getPuzzle(chengyu)]
    )

@app.route("/random")
def random():
    path = 'static/chengyu.json'
    chengyus = [select(path, 4) for i in range(10)]
    return render_template('index.html',
        title="10 Random puzzles",
        puzzles=[getPuzzle(chengyu) for chengyu in chengyus]
    )

