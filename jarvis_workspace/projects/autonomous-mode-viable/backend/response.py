from typing import Any, Dict, List, Optional, Union

class Response:
    def __init__(self, data: Optional[Any] = None, error: Optional[str] = None):
        self.data = data
        self.error = error

class Task:
    def __init__(self, name: str, description: str, complexity: int, research_first: bool):
        self.name = name
        self.description = description
        self.complexity = complexity
        self.research_first = research_first
        self.completed = False

class Decision:
    def __init__(self, task: Task, why: str):
        self.task = task
        self.why = why
        self.completed = False

class UserPreferences:
    def __init__(self, code_style: Dict[str, Any], design_standards: Dict[str, Any], writing_standards: Dict[str, Any]):
        self.code_style = code_style
        self.design_standards = design_standards
        self.writing_standards = writing_standards

class User:
    def __init__(self, name: str, preferences: Optional[UserPreferences] = None):
        self.name = name
        self.preferences = preferences or UserPreferences({})