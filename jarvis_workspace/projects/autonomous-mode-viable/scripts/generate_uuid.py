import os
import uuid

# Generate a random UUID
def generate_uuid():
    return str(uuid.uuid4())

# Generate a random UUID with a specific prefix
def generate_uuid_with_prefix(prefix):
    return f"{prefix}-{generate_uuid()}"

# Generate a random UUID with a specific path and prefix
def generate_uuid_with_path(path):
    return os.path.join(path, generate_uuid())