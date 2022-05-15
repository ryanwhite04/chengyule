from json import loads
from hashlib import sha256

def getIndex(digest, index, length, mod):
    return int.from_bytes(digest[index:index+length], 'little') % mod

def select(path, key, count=1):
    options = loads(open(path, encoding ="utf-8").read())
    digest = sha256(bytes(key)).digest()
    return [options[getIndex(digest, i*2, 2, len(options))] for i in range(count)]