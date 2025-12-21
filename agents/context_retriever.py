"""
Context Retriever for Jarvis v3
On-demand context retrieval (RAG-style) - agent asks for what it needs.
No more pre-loading with arbitrary token limits!

Flow:
1. Agent gets task summary
2. ContextRetriever asks LLM: "What files do you need?"
3. Only loads those specific files
4. Passes to agent with full content (no truncation)
"""
import os
import json
import requests
from typing import Dict, List, Optional
from .config import CONTEXT_DIR, LM_STUDIO_URL, WORKSPACE_DIR
from .code_indexer import code_indexer


class ContextRetriever:
    """
    On-demand context retrieval system.
    
    Instead of pre-loading all context with token limits,
    this asks the LLM which files are actually needed for the task.
    """
    
    # Available context file types
    CONTEXT_FILES = {
        "frontend_context.md": "UI components, React/CSS decisions, layout changes",
        "backend_context.md": "API routes, server logic, authentication",
        "database_context.md": "Schema, queries, migrations",
        "research_context.md": "Research notes, findings, sources",
        "decisions_context.md": "Architectural and design decisions",
        "architecture_context.md": "System design, component diagrams",
        "codebase_map.md": "Project file structure overview",
        "qa_context.md": "Testing notes, bug reports",
        "deployment_context.md": "DevOps, CI/CD, server configs",
        "task_state.md": "Current task progress and objectives",
    }
    
    def __init__(self):
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create context files if they don't exist."""
        os.makedirs(CONTEXT_DIR, exist_ok=True)
        for filename, description in self.CONTEXT_FILES.items():
            filepath = os.path.join(CONTEXT_DIR, filename)
            if not os.path.exists(filepath):
                name = filename.replace("_context.md", "").replace(".md", "").upper()
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {name} Context\n\n")
    
    def get_context_for_task(self, task: str, agent_name: str = None, 
                             project_path: str = None) -> str:
        """
        Main entry point: Get relevant context for a task.
        
        1. Reads task summary
        2. Asks LLM which files are needed
        3. Loads only those files
        4. Optionally indexes codebase if project_path provided
        """
        context_parts = []
        
        # Always include active task (small, essential)
        task_state = self._read_file("task_state.md")
        if task_state.strip():
            context_parts.append(f"## CURRENT TASK STATE\n{task_state}")
        
        # Ask LLM which context files are needed
        needed_files = self._ask_llm_for_needed_files(task, agent_name)
        
        # Load only the needed files
        for filename in needed_files:
            content = self._read_file(filename)
            if content.strip() and len(content) > 50:
                name = filename.replace("_context.md", "").replace(".md", "").upper()
                context_parts.append(f"## {name}\n{content}")
        
        # If project path provided, get relevant code context
        if project_path and os.path.exists(project_path):
            code_context = code_indexer.get_relevant_context(project_path, task)
            if code_context:
                context_parts.append(f"## CODE CONTEXT\n{code_context}")
        
        if context_parts:
            return "\n\n---\n\n".join(context_parts)
        return ""
    
    def _ask_llm_for_needed_files(self, task: str, agent_name: str = None) -> List[str]:
        """
        Ask the LLM which context files are relevant for this task.
        This is the RAG query step.
        """
        # Build file list for LLM
        file_list = "\n".join([f"- {k}: {v}" for k, v in self.CONTEXT_FILES.items()])
        
        prompt = f"""You are a context selector. Given a task, select which context files are relevant.

TASK: {task}
AGENT: {agent_name or "general"}

AVAILABLE CONTEXT FILES:
{file_list}

Select 1-3 files that are most relevant. Return ONLY a JSON array, nothing else:
["file1.md", "file2.md"]

If no files are clearly relevant, return: ["task_state.md"]
"""
        
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                    "temperature": 0
                },
                timeout=10
            )
            
            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"].strip()
                # Parse JSON array
                if reply.startswith("["):
                    files = json.loads(reply)
                    # Validate files exist in our list
                    return [f for f in files if f in self.CONTEXT_FILES]
        except:
            pass
        
        # Fallback: keyword-based selection
        return self._keyword_file_selection(task, agent_name)
    
    def _keyword_file_selection(self, task: str, agent_name: str = None) -> List[str]:
        """Fallback: select files based on keywords if LLM fails."""
        task_lower = task.lower()
        selected = []
        
        # Mapping of keywords to files
        keyword_map = {
            "frontend_context.md": ["ui", "react", "css", "component", "button", "page", "style"],
            "backend_context.md": ["api", "server", "route", "endpoint", "backend", "auth"],
            "database_context.md": ["database", "query", "schema", "sql", "table", "db"],
            "research_context.md": ["research", "paper", "study", "analyze", "find"],
            "decisions_context.md": ["decision", "choose", "why", "design", "architecture"],
            "codebase_map.md": ["code", "file", "project", "structure", "edit", "modify"],
            "deployment_context.md": ["deploy", "server", "host", "ci", "cd", "docker"],
        }
        
        for filename, keywords in keyword_map.items():
            if any(kw in task_lower for kw in keywords):
                selected.append(filename)
        
        return selected[:3] if selected else ["task_state.md"]
    
    def _read_file(self, filename: str) -> str:
        """Read a context file."""
        filepath = os.path.join(CONTEXT_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read()
            except:
                pass
        return ""
    
    def save_to_context(self, filename: str, content: str, 
                        agent_name: str = None, append: bool = True):
        """Save content to a context file."""
        if filename not in self.CONTEXT_FILES:
            filename = "decisions_context.md"  # Default
        
        filepath = os.path.join(CONTEXT_DIR, filename)
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        source = f" ({agent_name})" if agent_name else ""
        
        entry = f"\n### [{timestamp}]{source}\n{content}\n"
        
        if append:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(entry)
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(entry)
    
    def index_codebase(self, project_path: str) -> Dict:
        """Index a codebase for context retrieval."""
        return code_indexer.index_project(project_path)
    
    def get_code_context(self, project_path: str, task: str) -> str:
        """Get relevant code context for a task."""
        return code_indexer.get_relevant_context(project_path, task)
    
    def get_file_content(self, project_path: str, file_path: str) -> Optional[str]:
        """Read a specific file from a project."""
        return code_indexer.read_file(project_path, file_path)
    
    def edit_code(self, project_path: str, file_path: str, 
                  old_content: str, new_content: str) -> Dict:
        """Edit a file in a project (with automatic re-indexing)."""
        return code_indexer.edit_file(project_path, file_path, old_content, new_content)
    
    def get_status(self) -> Dict:
        """Get retriever status."""
        files_with_content = 0
        total_chars = 0
        
        for filename in self.CONTEXT_FILES:
            content = self._read_file(filename)
            if content.strip():
                files_with_content += 1
                total_chars += len(content)
        
        return {
            "context_files": len(self.CONTEXT_FILES),
            "files_with_content": files_with_content,
            "total_chars": total_chars,
            "indexed_projects": len(code_indexer.indexes)
        }


# Singleton
context_retriever = ContextRetriever()


# Convenience functions
def get_context(task: str, agent: str = None, project: str = None) -> str:
    """Get on-demand context for a task."""
    return context_retriever.get_context_for_task(task, agent, project)


def save_context(filename: str, content: str, agent: str = None):
    """Save content to a context file."""
    context_retriever.save_to_context(filename, content, agent)


def index_project(path: str) -> Dict:
    """Index a project for code context."""
    return context_retriever.index_codebase(path)
