import hashlib

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def md5(data):
    return hashlib.md5(data).hexdigest()