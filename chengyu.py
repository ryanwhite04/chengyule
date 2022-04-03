import json
# from random import choice
from hashlib import sha256
from datetime import datetime

def getIndex(digest, index, length, mod):
    return int.from_bytes(digest[index:index+length], 'little') % mod

def choose(options, count=1, key=b''):
    day = datetime.now().toordinal()
    digest = sha256(bytes(day)+key).digest()
    return [options[getIndex(digest, i*2, 2, len(options))] for i in range(count)]

def select(path):
    with open(path) as file:
        return choose(json.load(file), 4)

if __name__ == "__main__":
    print(select('static/chengyu.json'))
