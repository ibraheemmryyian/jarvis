import hashlib

def hash_md5(data):
    return hashlib.md5(data.encode()).hexdigest()

def hash_sha1(data):
    return hashlib.sha1(data.encode()).hexdigest()

def hash_sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

def hash_sha512(data):
    return hashlib.sha512(data.encode()).hexdigest()