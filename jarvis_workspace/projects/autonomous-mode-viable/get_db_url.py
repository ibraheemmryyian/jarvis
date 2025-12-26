import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "test.db")