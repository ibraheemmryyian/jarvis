import pydantic
from pydantic import ValidationError

try:
    config = JarvisConfig(**config_dict)
except ValidationError as e:
    print(f"Error loading configuration: {e}")