"""
Jarvis v2 Configuration
Centralized settings for all agents.
"""
import os

# --- LLM Server ---
LM_STUDIO_URL = os.environ.get("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(BASE_DIR, "jarvis_workspace")
CONTEXT_DIR = os.path.join(WORKSPACE_DIR, ".context")

# Ensure directories exist
os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(CONTEXT_DIR, exist_ok=True)

# --- Context Files ---
CONTEXT_FILES = {
    "active_task": os.path.join(CONTEXT_DIR, "active_task.md"),
    "research_notes": os.path.join(CONTEXT_DIR, "research_notes.md"),
    "codebase_map": os.path.join(CONTEXT_DIR, "codebase_map.md"),
    "decisions": os.path.join(CONTEXT_DIR, "decisions.md"),
    "deployment_log": os.path.join(CONTEXT_DIR, "deployment_log.md"),
    "documentation": os.path.join(CONTEXT_DIR, "documentation.md"),
    "user_preferences": os.path.join(CONTEXT_DIR, "user_preferences.md"),
}

# --- Agent Settings ---
AGENT_TEMPS = {
    "router": 0.0,      # Deterministic routing
    "research": 0.3,    # Slightly creative for synthesis
    "coder": 0.0,       # Precise code generation
    "ops": 0.0,         # Deterministic deployment
}

# --- Token Limits (Adaptive for Speed) ---
MAX_CONTEXT_TOKENS = int(os.environ.get("JARVIS_MAX_TOKENS", 32000))

# Adaptive output limits by task type
TOKEN_LIMITS = {
    "planning": 4096,
    "simple": 4096,
    "standard": 6144,
    "component": 10240,
    "max": 16384,
}

# Default for backward compatibility
MAX_OUTPUT_TOKENS = TOKEN_LIMITS["standard"]


# --- Runtime Context Settings ---
class ContextSettings:
    """
    Runtime-adjustable context settings.
    Can be modified from UI without restarting Jarvis.
    """
    def __init__(self):
        self._max_tokens = MAX_CONTEXT_TOKENS
        self._recycle_threshold = 0.75  # Recycle at 75% usage
        self._model_name = os.environ.get("JARVIS_MODEL", "nous-hermes-3-8b")
    
    @property
    def max_tokens(self) -> int:
        return self._max_tokens
    
    @max_tokens.setter
    def max_tokens(self, value: int):
        self._max_tokens = max(4096, min(value, 131072))  # Clamp 4K-128K
    
    @property
    def recycle_threshold(self) -> float:
        return self._recycle_threshold
    
    @recycle_threshold.setter
    def recycle_threshold(self, value: float):
        self._recycle_threshold = max(0.5, min(value, 0.95))  # Clamp 50%-95%
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @model_name.setter 
    def model_name(self, value: str):
        self._model_name = value
    
    def to_dict(self) -> dict:
        """Export settings for API/UI."""
        return {
            "max_tokens": self._max_tokens,
            "recycle_threshold": self._recycle_threshold,
            "model_name": self._model_name,
            "token_limits": TOKEN_LIMITS,
        }
    
    def update(self, **kwargs):
        """Update settings from dict (e.g., from API request)."""
        if "max_tokens" in kwargs:
            self.max_tokens = kwargs["max_tokens"]
        if "recycle_threshold" in kwargs:
            self.recycle_threshold = kwargs["recycle_threshold"]
        if "model_name" in kwargs:
            self.model_name = kwargs["model_name"]


# Global settings instance (modifiable at runtime)
context_settings = ContextSettings()

