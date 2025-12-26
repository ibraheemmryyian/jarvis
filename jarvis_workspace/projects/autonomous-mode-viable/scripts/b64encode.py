import base64

def b64encode(data):
    return base64.b64encode(data).decode('utf-8')

def b64decode(data):
    return base64.b64decode(data)

def urlsafe_b64encode(data):
    return b64encode(data).replace('=', '')

def urlsafe_b64decode(data):
    padding = len(data) % 4
    if padding == 2:
        data += '=='
    elif padding == 3:
        data += '='
    return b64decode(data)