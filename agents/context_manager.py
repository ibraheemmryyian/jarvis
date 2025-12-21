"""
Context Manager for Jarvis v2
Handles loading/saving task-specific .md files to control context window.
"""
import os
from datetime import datetime
from .config import CONTEXT_DIR, CONTEXT_FILES, MAX_CONTEXT_TOKENS


class ContextManager:
    """Manages context files for efficient LLM token usage."""
    
    def __init__(self):
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create empty context files if they don't exist."""
        for name, path in CONTEXT_FILES.items():
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"# {name.replace('_', ' ').title()}\n\n")
    
    # --- Read Operations ---
    
    def read(self, file_key: str) -> str:
        """Read a specific context file."""
        path = CONTEXT_FILES.get(file_key)
        if not path or not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    
    def read_active_task(self) -> str:
        """Always load the active task (small, fits in any context)."""
        return self.read("active_task")
    
    def read_for_agent(self, agent_type: str) -> str:
        """Load context files relevant to a specific agent using registry."""
        # Try to get agent-specific domains from registry
        try:
            from .registry import registry
            domains = registry.get_domains_for_agent(agent_type)
            if domains:
                combined = ""
                for domain in domains:
                    content = self._read_domain(domain)
                    if content.strip():
                        combined += f"\n\n---\n## {domain.upper()}\n{content}"
                return self._truncate_if_needed(combined)
        except:
            pass
        
        # Fallback: comprehensive mapping for all agent categories
        files_to_load = {
            # Frontend
            "frontend_dev": ["active_task", "frontend", "decisions"],
            "uiux": ["active_task", "frontend", "decisions"],
            "seo": ["active_task", "frontend", "content"],
            # Backend
            "backend_dev": ["active_task", "backend", "database"],
            "coder": ["active_task", "codebase_map", "decisions", "backend"],
            "ai_ops": ["active_task", "backend", "research"],
            "ai_infra": ["active_task", "backend", "deployment"],
            # Architecture
            "architect": ["active_task", "architecture", "decisions", "codebase_map"],
            "product_manager": ["active_task", "decisions", "research"],
            "strategy": ["active_task", "research", "decisions"],
            "business_analyst": ["active_task", "research"],
            # Research
            "researcher": ["active_task", "research_notes", "research"],
            "academic_research": ["active_task", "research"],
            "academic_workflow": ["active_task", "research"],
            # QA
            "qa_agent": ["active_task", "qa", "codebase_map"],
            "code_reviewer": ["active_task", "codebase_map", "decisions"],
            "security_auditor": ["active_task", "codebase_map"],
            # Ops
            "ops": ["active_task", "deployment_log", "deployment"],
            "git_agent": ["active_task", "codebase_map"],
            "terminal": ["active_task"],
            # Core
            "router": ["active_task"],
            "autonomous": ["active_task", "task_state", "decisions"],
        }
        
        keys = files_to_load.get(agent_type, ["active_task"])
        combined = ""
        for key in keys:
            content = self.read(key)
            if content.strip():
                combined += f"\n\n---\n## {key.upper()}\n{content}"
        
        return self._truncate_if_needed(combined)
    
    def _read_domain(self, domain: str) -> str:
        """Read a domain context file."""
        from .config import CONTEXT_DIR
        filepath = os.path.join(CONTEXT_DIR, f"{domain}_context.md")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    def _truncate_if_needed(self, text: str) -> str:
        """Rough truncation to stay under token limit (4 chars ≈ 1 token)."""
        max_chars = MAX_CONTEXT_TOKENS * 4
        if len(text) > max_chars:
            return text[:max_chars] + "\n\n[... TRUNCATED ...]"
        return text
    
    # --- Write Operations ---
    
    def write(self, file_key: str, content: str):
        """Overwrite a context file."""
        path = CONTEXT_FILES.get(file_key)
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def append(self, file_key: str, content: str):
        """Append to a context file with timestamp."""
        path = CONTEXT_FILES.get(file_key)
        if not path:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n\n### [{timestamp}]\n{content}")
    
    # --- Task Management ---
    
    def set_active_task(self, objective: str, subtasks: list = None):
        """Initialize or update the active task."""
        content = f"# Active Task\n\n## Objective\n{objective}\n\n"
        if subtasks:
            content += "## Subtasks\n"
            for i, task in enumerate(subtasks, 1):
                content += f"- [ ] {task}\n"
        content += f"\n## Status\nIn Progress\n\n## Started\n{datetime.now().isoformat()}\n"
        self.write("active_task", content)
    
    def mark_task_complete(self, summary: str):
        """Mark the active task as complete."""
        content = self.read("active_task")
        content = content.replace("## Status\nIn Progress", f"## Status\nComplete\n\n## Summary\n{summary}")
        content += f"\n\n## Completed\n{datetime.now().isoformat()}\n"
        self.write("active_task", content)
    
    def log_decision(self, decision: str, rationale: str):
        """Log a design decision to decisions.md."""
        entry = f"**Decision**: {decision}\n**Why**: {rationale}"
        self.append("decisions", entry)
    
    def update_codebase_map(self, project_path: str):
        """Scan a project and update the codebase map."""
        tree = self._generate_tree(project_path)
        self.write("codebase_map", f"# Codebase Map\n\n```\n{tree}\n```")
    
    def _generate_tree(self, path: str, prefix: str = "") -> str:
        """Generate a directory tree string."""
        if not os.path.exists(path):
            return f"{path} (not found)"
        
        entries = []
        try:
            items = sorted(os.listdir(path))
            # Filter out common noise
            items = [i for i in items if i not in ["node_modules", "__pycache__", ".git", "venv", ".venv"]]
            
            for i, item in enumerate(items[:20]):  # Limit to 20 items
                is_last = (i == len(items) - 1) or (i == 19)
                connector = "└── " if is_last else "├── "
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    entries.append(f"{prefix}{connector}{item}/")
                    if i < 10:  # Only recurse for first 10 dirs
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        entries.append(self._generate_tree(item_path, new_prefix))
                else:
                    entries.append(f"{prefix}{connector}{item}")
        except PermissionError:
            return f"{prefix}[Permission Denied]"
        
        return "\n".join(entries)


# Singleton instance
context = ContextManager()
