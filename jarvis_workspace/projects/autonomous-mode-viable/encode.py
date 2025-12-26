import base64

def encode(data):
    return base64.b64encode(data).decode()