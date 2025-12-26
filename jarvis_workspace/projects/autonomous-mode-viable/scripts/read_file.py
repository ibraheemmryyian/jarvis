import os
from typing import List, Dict, Any

def read_file(path: str) -> str:
    with open(path, 'r') as file:
        return file.read()

def write_file(path: str, content: str) -> None:
    with open(path, 'w') as file:
        file.write(content)

def load_json(file_path: str) -> Dict[str, Any]:
    import json
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data: Dict[str, Any], file_path: str) -> None:
    import json
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def list_files(directory: str) -> List[str]:
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def read_dir(directory: str) -> List[str]:
    return os.listdir(directory)