from json import loads
from random import randbytes
from hashlib import sha256

def getIndex(digest, index, length, mod):
    return int.from_bytes(digest[index:index+length], 'little') % mod

def select(path, count=1, key=b''):
    with open(path, encoding ="utf-8") as file:
        options = loads(file.read())
    digest = sha256(key or randbytes(32)).digest()
    return [options[getIndex(digest, i*2, 2, len(options))] for i in range(count)]  

if __name__ == "__main__":
    print(select('static/chengyu.json'))
