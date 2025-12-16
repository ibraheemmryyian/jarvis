"""
Context Recycler for Jarvis v2
Self-healing context management with auto-summarization and continuation.

"Can't outsmart the AI, but we can out-work it"
"""
import os
import json
import tiktoken
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .config import CONTEXT_DIR, MAX_CONTEXT_TOKENS
from .context_manager import context


class ContextRecycler:
    """
    Manages context window to prevent overflow.
    Auto-summarizes and generates continuation prompts.
    """
    
    # Domain-specific context files
    DOMAINS = {
        "frontend": "frontend_context.md",
        "backend": "backend_context.md", 
        "database": "database_context.md",
        "research": "research_context.md",
        "decisions": "decisions_context.md",
        "task_state": "task_state.md"
    }
    
    def __init__(self, max_tokens: int = None, threshold: float = 0.75):
        self.max_tokens = max_tokens or MAX_CONTEXT_TOKENS
        self.threshold = threshold
        self.current_tokens = 0
        self.conversation_history = []
        self.task_objective = ""
        self.completed_steps = []
        self.pending_steps = []
        
        # Initialize tokenizer (cl100k_base works for most models)
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except:
            self.tokenizer = None
        
        self._ensure_domain_files()
    
    def _ensure_domain_files(self):
        """Create domain context files if they don't exist."""
        os.makedirs(CONTEXT_DIR, exist_ok=True)
        for domain, filename in self.DOMAINS.items():
            filepath = os.path.join(CONTEXT_DIR, filename)
            if not os.path.exists(filepath):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {domain.upper()} Context\n\n")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Fallback: rough estimate (4 chars per token)
        return len(text) // 4
    
    def get_total_context_tokens(self) -> int:
        """Calculate total tokens in current conversation."""
        total = 0
        for msg in self.conversation_history:
            total += self.count_tokens(msg.get("content", ""))
        return total
    
    def needs_recycling(self) -> bool:
        """Check if context needs to be recycled."""
        current = self.get_total_context_tokens()
        threshold_tokens = int(self.max_tokens * self.threshold)
        return current >= threshold_tokens
    
    def get_context_usage(self) -> Dict:
        """Get context usage stats."""
        current = self.get_total_context_tokens()
        return {
            "current_tokens": current,
            "max_tokens": self.max_tokens,
            "threshold_tokens": int(self.max_tokens * self.threshold),
            "usage_percent": round((current / self.max_tokens) * 100, 1),
            "needs_recycling": self.needs_recycling()
        }
    
    # === Domain Context Management ===
    
    def save_to_domain(self, domain: str, content: str, append: bool = True):
        """Save content to a domain-specific context file."""
        if domain not in self.DOMAINS:
            domain = "decisions"  # Default
        
        filepath = os.path.join(CONTEXT_DIR, self.DOMAINS[domain])
        mode = "a" if append else "w"
        
        with open(filepath, mode, encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%H:%M:%S")
            f.write(f"\n## [{timestamp}]\n{content}\n")
    
    def read_domain(self, domain: str) -> str:
        """Read content from a domain context file."""
        if domain not in self.DOMAINS:
            return ""
        
        filepath = os.path.join(CONTEXT_DIR, self.DOMAINS[domain])
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    def clear_domain(self, domain: str):
        """Clear a domain context file."""
        if domain in self.DOMAINS:
            filepath = os.path.join(CONTEXT_DIR, self.DOMAINS[domain])
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {domain.upper()} Context\n\n")
    
    def get_all_domain_context(self) -> str:
        """Get combined context from all domain files (summarized)."""
        combined = []
        for domain in self.DOMAINS:
            content = self.read_domain(domain)
            if content and len(content) > 100:
                # Only include last 2000 chars per domain to save tokens
                combined.append(f"### {domain.upper()}\n{content[-2000:]}")
        return "\n\n".join(combined)
    
    # === Task State Management ===
    
    def set_task(self, objective: str, steps: List[str] = None):
        """Set the current task objective and steps. Auto-clears old task."""
        # If this is a NEW task (different objective), clear the old one
        if self.task_objective and self.task_objective != objective:
            self._archive_old_task()
        
        self.task_objective = objective
        self.pending_steps = steps or []
        self.completed_steps = []
        
        # Generate unique task ID
        task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to task_state (overwrites old content)
        state = f"""# Task: {task_id}
        
**Objective:** {objective}

**Steps:**
{chr(10).join(f'- [ ] {s}' for s in self.pending_steps)}
"""
        self.save_to_domain("task_state", state, append=False)
    
    def _archive_old_task(self):
        """Archive the previous task before starting a new one."""
        old_state = self.read_domain("task_state")
        if old_state and len(old_state) > 100:
            archive_dir = os.path.join(CONTEXT_DIR, "archive")
            os.makedirs(archive_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = os.path.join(archive_dir, f"task_{timestamp}.md")
            
            with open(archive_path, "w", encoding="utf-8") as f:
                f.write(old_state)
    
    def mark_step_complete(self, step: str, result: str = ""):
        """Mark a step as complete."""
        if step in self.pending_steps:
            self.pending_steps.remove(step)
        self.completed_steps.append({"step": step, "result": result})
        
        # Update task_state
        self.save_to_domain("task_state", f"Completed: {step}\nResult: {result[:200]}")
    
    def get_progress(self) -> Dict:
        """Get task progress."""
        total = len(self.completed_steps) + len(self.pending_steps)
        completed = len(self.completed_steps)
        return {
            "objective": self.task_objective,
            "completed": completed,
            "remaining": len(self.pending_steps),
            "total": total,
            "percent": round((completed / total * 100) if total > 0 else 0, 1),
            "pending_steps": self.pending_steps,
            "completed_steps": [s["step"] for s in self.completed_steps]
        }
    
    # === Recycling ===
    
    def generate_summary_prompt(self) -> str:
        """Generate prompt to ask LLM to summarize current work."""
        progress = self.get_progress()
        return f"""Summarize the work done so far on this task.

OBJECTIVE: {progress['objective']}

COMPLETED STEPS ({progress['completed']}/{progress['total']}):
{chr(10).join(f'- {s}' for s in progress['completed_steps'])}

REMAINING STEPS:
{chr(10).join(f'- {s}' for s in progress['pending_steps'])}

Create a brief summary (under 500 words) that captures:
1. What was accomplished
2. Key decisions made
3. Any blockers or issues
4. Current state of each component (frontend/backend/database)

Output the summary directly, no formatting."""
    
    def generate_continuation_prompt(self, summary: str) -> str:
        """Generate the prompt that will continue the task with fresh context."""
        progress = self.get_progress()
        domain_context = self.get_all_domain_context()
        
        return f"""Continue this task from where it left off.

## OBJECTIVE
{progress['objective']}

## PROGRESS SUMMARY
{summary}

## REMAINING STEPS
{chr(10).join(f'- {s}' for s in progress['pending_steps'])}

## SAVED CONTEXT
{domain_context[:3000]}

Continue working on the next step. Do not repeat completed work."""
    
    def recycle(self, llm_call_func) -> str:
        """
        Execute the recycling process.
        
        Args:
            llm_call_func: Function to call LLM (takes prompt, returns response)
        
        Returns:
            Continuation prompt to start fresh context
        """
        print("[Recycler] Context at 75% - initiating recycle...")
        
        # Step 1: Ask LLM to summarize
        summary_prompt = self.generate_summary_prompt()
        summary = llm_call_func(summary_prompt)
        
        # Step 2: Save summary to domain files
        self.save_to_domain("decisions", f"### RECYCLE SUMMARY\n{summary}")
        
        # Categorize summary into domains (simple keyword matching)
        if "frontend" in summary.lower() or "react" in summary.lower() or "ui" in summary.lower():
            self.save_to_domain("frontend", summary[:1000])
        if "backend" in summary.lower() or "api" in summary.lower() or "server" in summary.lower():
            self.save_to_domain("backend", summary[:1000])
        if "database" in summary.lower() or "schema" in summary.lower() or "table" in summary.lower():
            self.save_to_domain("database", summary[:1000])
        
        # Step 3: Clear conversation history
        self.conversation_history = []
        
        # Step 4: Generate continuation prompt
        continuation = self.generate_continuation_prompt(summary)
        
        print(f"[Recycler] Generated continuation prompt ({self.count_tokens(continuation)} tokens)")
        
        return continuation


# Singleton
recycler = ContextRecycler()
