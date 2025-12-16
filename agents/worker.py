"""
Queue Worker Executor for Jarvis v2
Executes queued tasks using the appropriate agent.
"""
from typing import Dict, Any, Callable
from .queue import TaskType
from .synthesis import deep_research_v2
from .orchestrator import orchestrator


def execute_queued_task(
    task_type: str, 
    input_data: Dict[str, Any], 
    progress_callback: Callable
) -> Dict[str, Any]:
    """
    Execute a queued task based on its type.
    This is called by the queue worker.
    
    Args:
        task_type: Type of task (autonomous, research, build, deploy)
        input_data: Task parameters (topic, etc)
        progress_callback: Function to call with progress updates
    
    Returns:
        Result dictionary
    """
    topic = input_data.get("topic", "")
    
    if task_type == TaskType.AUTONOMOUS.value or task_type == "autonomous":
        # Full pipeline
        progress_callback("Starting autonomous pipeline...")
        return orchestrator.execute_autonomous(topic, progress_callback)
    
    elif task_type == TaskType.RESEARCH.value or task_type == "research":
        # Research only
        progress_callback("Starting brute force research...")
        return deep_research_v2(topic, progress_callback)
    
    elif task_type == TaskType.BUILD.value or task_type == "build":
        # Build only (use coder agent)
        progress_callback("Starting code generation...")
        from .coder import coder
        return {"code": coder.run(topic)}
    
    elif task_type == TaskType.DEPLOY.value or task_type == "deploy":
        # Deploy only
        progress_callback("Starting deployment planning...")
        from .ops import ops
        return {"deployment": ops.run(topic)}
    
    else:
        return {"error": f"Unknown task type: {task_type}"}


def start_queue_worker():
    """Start the background queue worker."""
    from .queue import task_queue
    task_queue.start_worker(execute_queued_task)


def stop_queue_worker():
    """Stop the background queue worker."""
    from .queue import task_queue
    task_queue.stop_worker()
