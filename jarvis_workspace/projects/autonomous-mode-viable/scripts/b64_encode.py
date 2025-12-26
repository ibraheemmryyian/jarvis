import base64

def b64_encode(data):
    return base64.b64encode(data).decode('utf-8')

def b64_decode(data):
    return base64.b64decode(data)

def url_safe_b64_encode(data):
    return base64.urlsafe_b64encode(data).decode('utf-8')

def url_safe_b64_decode(data):
    return base64.urlsafe_b64decode(data)