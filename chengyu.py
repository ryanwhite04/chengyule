import json
from random import choice

def select():
    with open('static/chengyu.json') as file:
        return choice(json.load(file))

if __name__ == "__main__":
    print(select())
