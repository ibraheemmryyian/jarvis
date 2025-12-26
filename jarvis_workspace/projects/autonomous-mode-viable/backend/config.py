from typing import Any, Dict, List, Optional, Union

# Custom types for project
class Config:
    def __init__(self, data: dict):
        self.data = data

class Task:
    def __init__(self, name: str, desc: str, complexity: int):
        self.name = name
        self.desc = desc
        self.complexity = complexity

class Decision:
    def __init__(self, decision: str, why: str):
        self.decision = decision
        self.why = why

# Project types
ProjectPath = Union[str, Path]
ActiveTask = Dict[str, Any]
Decisions = List[Decision]