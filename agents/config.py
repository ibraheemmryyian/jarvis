"""
Jarvis v2 Configuration
Centralized settings for all agents.
"""
import os

# --- LLM Server ---
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

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
    "user_preferences": os.path.join(CONTEXT_DIR, "user_preferences.md"),  # NEW: User preferences
}

# --- Agent Settings ---
AGENT_TEMPS = {
    "router": 0.0,      # Deterministic routing
    "research": 0.3,    # Slightly creative for synthesis
    "coder": 0.0,       # Precise code generation
    "ops": 0.0,         # Deterministic deployment
}

# --- Token Limits (Adaptive for Speed) ---
# Smaller limits for simple tasks, larger for complex code generation
MAX_CONTEXT_TOKENS = 132000

# Adaptive output limits by task type
TOKEN_LIMITS = {
    "planning": 4096,      # Plans, routing, analysis (~20 min at 3 t/s)
    "simple": 4096,        # Quick responses, summaries
    "standard": 6144,      # Most code tasks (~30 min at 3 t/s)
    "component": 10240,    # Full component generation (~55 min at 3 t/s)
    "max": 16384,          # Only for explicit "create complete app" steps
}

# Default for backward compatibility
MAX_OUTPUT_TOKENS = TOKEN_LIMITS["standard"]
