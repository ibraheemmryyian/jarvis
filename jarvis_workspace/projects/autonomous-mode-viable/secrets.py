import os

def get_secret(key: str) -> str:
    """
    Retrieves a secret value by key.
    
    Args:
        key (str): The unique identifier for the secret.
        
    Returns:
        str: The retrieved secret value, or None if not found.
    """
    secrets_path = os.path.join(os.getcwd(), 'secrets')
    if not os.path.exists(secrets_path):
        os.makedirs(secrets_path)
    
    secrets_file = os.path.join(secrets_path, 'secrets.env')
    
    if os.path.exists(secrets_file):
        with open(secrets_file) as f:
            for line in f:
                parts = line.strip().split('=', 1)
                if len(parts) == 2 and key == parts[0]:
                    return parts[1]
                    
    return None

def set_secret(key: str, value: str):
    """
    Stores a secret value by key.
    
    Args:
        key (str): The unique identifier for the secret.
        value (str): The secret value to store.
    """
    secrets_path = os.path.join(os.getcwd(), 'secrets')
    if not os.path.exists(secrets_path):
        os.makedirs(secrets_path)
        
    secrets_file = os.path.join(secrets_path, 'secrets.env')
    
    with open(secrets_file, 'a') as f:
        f.write(f'{key}={value}\n')

# Example usage
SECRET_KEY = "my_secret"
SECRET_VALUE = "s3cr3t"

# Set the secret value
set_secret(SECRET_KEY, SECRET_VALUE)

# Get the secret value
print(get_secret(SECRET_KEY))