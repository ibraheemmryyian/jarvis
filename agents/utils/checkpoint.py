"""
Checkpoint System for Jarvis Autonomous Execution
Enables crash recovery and session continuity.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from ..config import WORKSPACE_DIR


class CheckpointManager:
    """
    Manages execution checkpoints for crash recovery.
    
    Saves:
    - Current iteration
    - Completed steps
    - Pending steps
    - Objective
    - Timestamp
    - Any intermediate results
    """
    
    CHECKPOINT_DIR = os.path.join(WORKSPACE_DIR, "checkpoints")
    MAX_CHECKPOINTS = 10  # Keep last 10 checkpoints
    
    def __init__(self):
        os.makedirs(self.CHECKPOINT_DIR, exist_ok=True)
    
    def save_checkpoint(
        self,
        objective: str,
        iteration: int,
        completed_steps: List[str],
        pending_steps: List[str],
        project_path: str = None,
        metadata: Dict = None
    ) -> str:
        """Save execution state to checkpoint file."""
        checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        checkpoint = {
            "id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "objective": objective,
            "iteration": iteration,
            "completed_steps": completed_steps,
            "pending_steps": pending_steps,
            "project_path": project_path,
            "metadata": metadata or {},
            "version": "1.0"
        }
        
        filepath = os.path.join(self.CHECKPOINT_DIR, f"checkpoint_{checkpoint_id}.json")
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2)
        
        # Clean old checkpoints
        self._cleanup_old_checkpoints()
        
        return checkpoint_id
    
    def get_latest_checkpoint(self) -> Optional[Dict]:
        """Get the most recent checkpoint if exists."""
        checkpoints = self._list_checkpoints()
        
        if not checkpoints:
            return None
        
        # Sort by timestamp (filename contains timestamp)
        checkpoints.sort(reverse=True)
        latest_file = checkpoints[0]
        
        return self._load_checkpoint(latest_file)
    
    def get_checkpoint_by_id(self, checkpoint_id: str) -> Optional[Dict]:
        """Load a specific checkpoint by ID."""
        filepath = os.path.join(self.CHECKPOINT_DIR, f"checkpoint_{checkpoint_id}.json")
        
        if os.path.exists(filepath):
            return self._load_checkpoint(filepath)
        
        return None
    
    def list_checkpoints(self) -> List[Dict]:
        """List all available checkpoints with summaries."""
        checkpoints = []
        
        for filename in self._list_checkpoints():
            cp = self._load_checkpoint(os.path.join(self.CHECKPOINT_DIR, filename))
            if cp:
                checkpoints.append({
                    "id": cp["id"],
                    "timestamp": cp["timestamp"],
                    "objective": cp["objective"][:50] + "..." if len(cp["objective"]) > 50 else cp["objective"],
                    "iteration": cp["iteration"],
                    "completed": len(cp["completed_steps"]),
                    "pending": len(cp["pending_steps"])
                })
        
        return sorted(checkpoints, key=lambda x: x["timestamp"], reverse=True)
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint."""
        filepath = os.path.join(self.CHECKPOINT_DIR, f"checkpoint_{checkpoint_id}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        
        return False
    
    def clear_all_checkpoints(self) -> int:
        """Clear all checkpoints. Returns count deleted."""
        count = 0
        for filename in self._list_checkpoints():
            filepath = os.path.join(self.CHECKPOINT_DIR, filename)
            os.remove(filepath)
            count += 1
        
        return count
    
    def _list_checkpoints(self) -> List[str]:
        """List checkpoint files."""
        if not os.path.exists(self.CHECKPOINT_DIR):
            return []
        
        return [f for f in os.listdir(self.CHECKPOINT_DIR) 
                if f.startswith("checkpoint_") and f.endswith(".json")]
    
    def _load_checkpoint(self, filepath: str) -> Optional[Dict]:
        """Load checkpoint from file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    
    def _cleanup_old_checkpoints(self):
        """Keep only the latest MAX_CHECKPOINTS checkpoints."""
        checkpoints = self._list_checkpoints()
        
        if len(checkpoints) > self.MAX_CHECKPOINTS:
            checkpoints.sort()  # Oldest first
            to_delete = checkpoints[:-self.MAX_CHECKPOINTS]
            
            for filename in to_delete:
                filepath = os.path.join(self.CHECKPOINT_DIR, filename)
                try:
                    os.remove(filepath)
                except:
                    pass


# Singleton
checkpoint_manager = CheckpointManager()
