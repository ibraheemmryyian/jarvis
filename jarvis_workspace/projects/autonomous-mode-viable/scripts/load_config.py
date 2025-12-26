import os
import json
from typing import Any, Dict, List

# Constants
CONFIG_FILE = "config.json"
PROJECTS_DIR = "projects"

def load_config() -> Dict[str, Any]:
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def save_config(config: Dict[str, Any]) -> None:
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def list_projects() -> List[str]:
    return [project for project in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, project))]

def get_project_path(project_name: str) -> str:
    return os.path.join(PROJECTS_DIR, project_name)

def load_project_config(project_name: str) -> Dict[str, Any]:
    with open(get_project_path(project_name), "r") as file:
        return json.load(file)

def save_project_config(project_name: str, config: Dict[str, Any]) -> None:
    with open(get_project_path(project_name), "w") as file:
        json.dump(config, file, indent=4)