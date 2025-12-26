import os

# Load environment variables from .env file into environment
def load_dotenv():
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Attempt to load .env file
    try:
        import dotenv
        dotenv.load_dotenv()
        print("Loaded .env file successfully.")
    except FileNotFoundError:
        print("Error: .env file not found. Ensure it exists in the same directory as this script.")

# Load environment variables from .env file into os.environ
def load_env_vars():
    # Attempt to load env vars
    try:
        import os
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        print(f"Loading environment variables from {env_path}")
        import dotenv
        dotenv.load_dotenv(dotenv_path=env_path)
        print("Loaded .env file successfully.")
    except FileNotFoundError:
        print("Error: .env file not found. Ensure it exists in the same directory as this script.")

# Main function to run the loading of environment variables
def main():
    load_dotenv()
    load_env_vars()

if __name__ == "__main__":
    main()