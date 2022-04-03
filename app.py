from flask import Flask, render_template
from chengyu import select
from os import listdir

app = Flask(__name__)

@app.route("/chengyu")
def chegnyu():
    return select()

@app.route("/")
@app.route("/index")
def index():
    chengyu = select('static/chengyu.json')
    return render_template('index.html',
        options="".join([c["chinese"] for c in chengyu]),
        answer=chengyu[0]["chinese"],
        question=chengyu[0]["english"]
    )

