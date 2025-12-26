import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Add your settings here
    pass

settings = Settings()

def load_config():
    return settings