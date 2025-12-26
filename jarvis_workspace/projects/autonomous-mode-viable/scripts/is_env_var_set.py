import os

def is_env_var_set(env_var_name: str) -> bool:
    return env_var_name in os.environ