"""
Error Journal for Jarvis
Logs errors and learns from past mistakes to avoid repeating them.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from ..config import WORKSPACE_DIR


class ErrorJournal:
    """
    Tracks errors and their solutions for learning.
    
    Before each task, agent can check if similar errors occurred before
    and get guidance on how to avoid them.
    """
    
    JOURNAL_FILE = os.path.join(WORKSPACE_DIR, "error_journal.json")
    MAX_ENTRIES = 100
    
    def __init__(self):
        self.entries: List[Dict] = []
        self._load()
    
    def log_error(
        self,
        task_type: str,
        task_description: str,
        error: str,
        solution: str = None,
        stack_trace: str = None,
        agent: str = None
    ):
        """
        Log an error and optionally its solution.
        
        Args:
            task_type: Category of task (coding, research, etc.)
            task_description: What was being attempted
            error: The error message
            solution: How it was fixed (if known)
            stack_trace: Full stack trace for debugging
            agent: Which agent encountered the error
        """
        entry = {
            "id": len(self.entries) + 1,
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "task_description": task_description[:200],  # Truncate long descriptions
            "error": error,
            "error_keywords": self._extract_keywords(error),
            "solution": solution,
            "stack_trace": stack_trace,
            "agent": agent,
            "occurrences": 1
        }
        
        # Check if similar error exists
        similar = self._find_similar(error)
        if similar:
            similar["occurrences"] += 1
            similar["last_seen"] = datetime.now().isoformat()
            if solution and not similar.get("solution"):
                similar["solution"] = solution
        else:
            self.entries.append(entry)
        
        self._save()
    
    def log_solution(self, error_id: int, solution: str):
        """Add a solution to an existing error entry."""
        for entry in self.entries:
            if entry["id"] == error_id:
                entry["solution"] = solution
                entry["solved_at"] = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def get_relevant_errors(self, task: str, limit: int = 3) -> List[Dict]:
        """
        Get errors relevant to a task for preemptive guidance.
        
        Returns entries with similar keywords to help agent avoid past mistakes.
        """
        task_keywords = self._extract_keywords(task)
        
        scored = []
        for entry in self.entries:
            score = len(set(task_keywords) & set(entry.get("error_keywords", [])))
            if score > 0:
                scored.append((score, entry))
        
        # Sort by relevance score, then by occurrences
        scored.sort(key=lambda x: (x[0], x[1].get("occurrences", 1)), reverse=True)
        
        return [entry for _, entry in scored[:limit]]
    
    def get_avoid_instructions(self, task: str) -> str:
        """
        Generate AVOID instructions based on past errors.
        This is injected into agent prompts.
        """
        relevant = self.get_relevant_errors(task)
        
        if not relevant:
            return ""
        
        lines = ["## AVOID (Based on Past Errors):\n"]
        
        for entry in relevant:
            lines.append(f"- **{entry['error'][:100]}**")
            if entry.get("solution"):
                lines.append(f"  → Fix: {entry['solution'][:100]}")
            lines.append(f"  (occurred {entry.get('occurrences', 1)}x)")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict:
        """Get error statistics."""
        if not self.entries:
            return {"total": 0, "solved": 0, "unsolved": 0}
        
        solved = sum(1 for e in self.entries if e.get("solution"))
        
        # Most common errors
        sorted_by_occurrence = sorted(
            self.entries,
            key=lambda x: x.get("occurrences", 1),
            reverse=True
        )
        
        return {
            "total": len(self.entries),
            "solved": solved,
            "unsolved": len(self.entries) - solved,
            "most_common": [
                {"error": e["error"][:50], "count": e.get("occurrences", 1)}
                for e in sorted_by_occurrence[:5]
            ]
        }
    
    def clear_old_entries(self, days: int = 30):
        """Remove entries older than specified days."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        original_count = len(self.entries)
        self.entries = [
            e for e in self.entries
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        
        self._save()
        return original_count - len(self.entries)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from error text for matching."""
        import re
        
        # Common error-related words to extract
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text.lower())
        
        # Filter out very common words
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                     "in", "on", "at", "to", "for", "of", "and", "or", "not"}
        
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        return list(set(keywords))[:20]  # Limit to 20 keywords
    
    def _find_similar(self, error: str) -> Optional[Dict]:
        """Find similar existing error entry."""
        error_keywords = set(self._extract_keywords(error))
        
        for entry in self.entries:
            existing_keywords = set(entry.get("error_keywords", []))
            # Consider similar if >50% keyword overlap
            overlap = len(error_keywords & existing_keywords)
            if overlap > len(error_keywords) * 0.5:
                return entry
        
        return None
    
    def _load(self):
        """Load journal from disk."""
        if os.path.exists(self.JOURNAL_FILE):
            try:
                with open(self.JOURNAL_FILE, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except:
                self.entries = []
    
    def _save(self):
        """Save journal to disk."""
        os.makedirs(os.path.dirname(self.JOURNAL_FILE), exist_ok=True)
        
        # Keep only last MAX_ENTRIES
        if len(self.entries) > self.MAX_ENTRIES:
            self.entries = self.entries[-self.MAX_ENTRIES:]
        
        with open(self.JOURNAL_FILE, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2)


# Singleton
error_journal = ErrorJournal()


def log_error(task_type: str, task: str, error: str, solution: str = None):
    """Convenience function to log an error."""
    error_journal.log_error(task_type, task, error, solution)


def get_avoid_instructions(task: str) -> str:
    """Convenience function to get avoid instructions."""
    return error_journal.get_avoid_instructions(task)
