import os

# Load environment variables from .env file
load_dotenv()

class Dotenv:
    def __init__(self):
        self.env_vars = {}
    
    def load(self, path=".env"):
        """Load environment variables from a .env file."""
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.strip().split("=", 1)
                    self.env_vars[key] = os.getenv(key, default=value)
    
    def get(self, key):
        """Get the value of an environment variable."""
        return self.env_vars.get(key)

# Usage: 
# import dotenv
# dotenv.load()
# value = dotenv.get('MY_VARIABLE')