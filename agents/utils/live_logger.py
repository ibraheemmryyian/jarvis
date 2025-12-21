"""
Live Logger for Jarvis
Real-time progress visibility during autonomous execution.
"""
import sys
import time
from datetime import datetime
from typing import Optional

class LiveLogger:
    """Real-time progress logger with flush for immediate output."""
    
    def __init__(self, name: str = "Jarvis"):
        self.name = name
        self.start_time = time.time()
        self.step_count = 0
        self.current_step = ""
        
    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")
    
    def _elapsed(self) -> str:
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        return f"{mins:02d}:{secs:02d}"
    
    def log(self, message: str, level: str = "INFO"):
        """Log with immediate flush."""
        prefix = {
            "INFO": "ℹ️",
            "START": "🚀",
            "STEP": "📍",
            "LLM": "🤖",
            "FILE": "📄",
            "DONE": "✅",
            "ERROR": "❌",
            "WARN": "⚠️",
        }.get(level, "•")
        
        print(f"[{self._timestamp()}] [{self._elapsed()}] {prefix} {message}", flush=True)
    
    def start_task(self, objective: str):
        """Log task start."""
        self.start_time = time.time()
        self.log(f"Starting: {objective[:80]}...", "START")
    
    def start_step(self, step: str):
        """Log step start."""
        self.step_count += 1
        self.current_step = step
        self.log(f"Step {self.step_count}: {step[:60]}...", "STEP")
    
    def llm_start(self, agent: str = "autonomous"):
        """Log LLM call start."""
        self.log(f"[{agent}] Calling LLM...", "LLM")
    
    def llm_done(self, tokens: int = 0):
        """Log LLM call complete."""
        msg = f"LLM response received"
        if tokens > 0:
            msg += f" ({tokens} tokens)"
        self.log(msg, "LLM")
    
    def file_saved(self, filename: str):
        """Log file save."""
        self.log(f"Saved: {filename}", "FILE")
    
    def error(self, message: str):
        """Log error."""
        self.log(message, "ERROR")
    
    def done(self, summary: str = ""):
        """Log completion."""
        self.log(f"Complete! {summary}", "DONE")
    
    def progress(self, current: int, total: int, label: str = ""):
        """Log progress bar."""
        pct = int((current / total) * 100) if total > 0 else 0
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        self.log(f"{label} [{bar}] {pct}% ({current}/{total})", "INFO")


# Global instance
live_logger = LiveLogger()
