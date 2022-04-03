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
    return render_template('index.html')

