class Settings(BaseSettings):
    # ... rest of the code ...

    class Config:
        env_file = ".env"