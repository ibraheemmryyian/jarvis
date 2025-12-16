"""
Background Task Queue for Jarvis v2
Persistent SQLite queue for long-horizon tasks.
"Queue it and walk away"
"""
import os
import json
import sqlite3
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from .config import WORKSPACE_DIR
from .notifications import notify_task_complete, notify_error


# Queue database path
QUEUE_DIR = os.path.join(WORKSPACE_DIR, ".queue")
QUEUE_DB = os.path.join(QUEUE_DIR, "tasks.db")


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(Enum):
    AUTONOMOUS = "autonomous"      # Full research → build → deploy
    RESEARCH = "research"          # Just brute force research
    BUILD = "build"                # Just code generation
    DEPLOY = "deploy"              # Just deployment


@dataclass
class QueuedTask:
    """A task in the queue."""
    id: int
    task_type: str
    input_data: str              # JSON string of input parameters
    status: str
    result: Optional[str]        # JSON string of result
    error: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    progress: str                # Latest progress message


class TaskQueue:
    """
    Persistent SQLite queue for long-horizon tasks.
    Survives app restarts.
    """
    
    def __init__(self):
        os.makedirs(QUEUE_DIR, exist_ok=True)
        self._init_db()
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self._current_task_id: Optional[int] = None
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(QUEUE_DB)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                input_data TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                result TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                progress TEXT DEFAULT ''
            )
        ''')
        conn.commit()
        conn.close()
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get a new connection (thread-safe)."""
        return sqlite3.connect(QUEUE_DB)
    
    # === QUEUE OPERATIONS ===
    
    def add(self, task_type: TaskType, input_data: Dict) -> int:
        """Add a task to the queue. Returns task ID."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (task_type, input_data, status, created_at)
            VALUES (?, ?, ?, ?)
        ''', (
            task_type.value,
            json.dumps(input_data),
            TaskStatus.PENDING.value,
            datetime.now().isoformat()
        ))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        print(f"[Queue] Task #{task_id} added: {task_type.value}")
        return task_id
    
    def get_next_pending(self) -> Optional[QueuedTask]:
        """Get the next pending task."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status = ? 
            ORDER BY created_at ASC 
            LIMIT 1
        ''', (TaskStatus.PENDING.value,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return QueuedTask(
                id=row[0], task_type=row[1], input_data=row[2],
                status=row[3], result=row[4], error=row[5],
                created_at=row[6], started_at=row[7],
                completed_at=row[8], progress=row[9] or ""
            )
        return None
    
    def update_status(self, task_id: int, status: TaskStatus, 
                      result: str = None, error: str = None):
        """Update task status."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        updates = ["status = ?"]
        values = [status.value]
        
        if status == TaskStatus.RUNNING:
            updates.append("started_at = ?")
            values.append(datetime.now().isoformat())
        
        if status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            updates.append("completed_at = ?")
            values.append(datetime.now().isoformat())
        
        if result:
            updates.append("result = ?")
            values.append(result)
        
        if error:
            updates.append("error = ?")
            values.append(error)
        
        values.append(task_id)
        cursor.execute(f'''
            UPDATE tasks SET {", ".join(updates)} WHERE id = ?
        ''', values)
        conn.commit()
        conn.close()
    
    def update_progress(self, task_id: int, progress: str):
        """Update task progress message."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks SET progress = ? WHERE id = ?
        ''', (progress, task_id))
        conn.commit()
        conn.close()
    
    def get_all(self, limit: int = 20) -> List[QueuedTask]:
        """Get all tasks (newest first)."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            QueuedTask(
                id=row[0], task_type=row[1], input_data=row[2],
                status=row[3], result=row[4], error=row[5],
                created_at=row[6], started_at=row[7],
                completed_at=row[8], progress=row[9] or ""
            )
            for row in rows
        ]
    
    def get_pending_count(self) -> int:
        """Get count of pending tasks."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM tasks WHERE status = ?
        ''', (TaskStatus.PENDING.value,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # === WORKER ===
    
    def start_worker(self, task_executor: Callable):
        """Start the background worker thread."""
        if self._running:
            return
        
        self._running = True
        self._task_executor = task_executor
        self._worker_thread = threading.Thread(
            target=self._worker_loop, 
            daemon=True,
            name="JarvisQueueWorker"
        )
        self._worker_thread.start()
        print("[Queue] Worker started")
    
    def stop_worker(self):
        """Stop the worker thread."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        print("[Queue] Worker stopped")
    
    def _worker_loop(self):
        """Main worker loop - processes tasks one at a time."""
        while self._running:
            task = self.get_next_pending()
            
            if task:
                self._current_task_id = task.id
                print(f"[Queue] Processing Task #{task.id}: {task.task_type}")
                
                # Update status to running
                self.update_status(task.id, TaskStatus.RUNNING)
                
                try:
                    # Parse input data
                    input_data = json.loads(task.input_data)
                    
                    # Progress callback
                    def progress_callback(msg):
                        self.update_progress(task.id, msg)
                    
                    # Execute the task
                    result = self._task_executor(
                        task.task_type, 
                        input_data, 
                        progress_callback
                    )
                    
                    # Mark as completed
                    self.update_status(
                        task.id, 
                        TaskStatus.COMPLETED,
                        result=json.dumps(result) if result else None
                    )
                    
                    # Notify user
                    notify_task_complete(
                        f"Task #{task.id} Complete",
                        input_data.get("topic", "")[:50]
                    )
                    print(f"[Queue] Task #{task.id} completed!")
                    
                except Exception as e:
                    # Mark as failed
                    self.update_status(
                        task.id, 
                        TaskStatus.FAILED,
                        error=str(e)
                    )
                    notify_error(f"Task #{task.id} failed: {str(e)[:50]}")
                    print(f"[Queue] Task #{task.id} failed: {e}")
                
                self._current_task_id = None
            else:
                # No pending tasks, sleep
                time.sleep(5)
    
    @property
    def is_busy(self) -> bool:
        """Check if worker is processing a task."""
        return self._current_task_id is not None


# Singleton
task_queue = TaskQueue()


def queue_autonomous(topic: str) -> int:
    """Queue an autonomous (research → build → deploy) task."""
    return task_queue.add(TaskType.AUTONOMOUS, {"topic": topic})


def queue_research(topic: str) -> int:
    """Queue a research-only task."""
    return task_queue.add(TaskType.RESEARCH, {"topic": topic})


def get_queue_status() -> Dict:
    """Get current queue status for UI."""
    tasks = task_queue.get_all(10)
    return {
        "pending": task_queue.get_pending_count(),
        "is_busy": task_queue.is_busy,
        "current_task_id": task_queue._current_task_id,
        "recent_tasks": [
            {
                "id": t.id,
                "type": t.task_type,
                "status": t.status,
                "progress": t.progress,
                "created": t.created_at
            }
            for t in tasks
        ]
    }
