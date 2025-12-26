from . import settings

class BaseSettings:
    SECRET_KEY: str = settings.SECRET_KEY
    ALGORITHM: str = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES