import base64

class Base64:
    @staticmethod
    def b64encode(data: str) -> str:
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    @staticmethod
    def b64decode(data: str) -> str:
        return base64.b64decode(data).decode('utf-8')