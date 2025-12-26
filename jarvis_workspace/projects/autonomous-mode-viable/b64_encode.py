import base64

def encode(data):
    return base64.b64encode(data).decode()

def decode(data):
    return base64.b64decode(data)

if __name__ == "__main__":
    message_bytes = "Hello World".encode()
    encoded_message = encode(message_bytes)
    print(encoded_message)
    decoded_message = decode(encoded_message)
    print(decoded_message)