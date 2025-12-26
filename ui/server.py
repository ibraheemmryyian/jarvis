"""
Jarvis Web UI - FastAPI Backend
Provides API endpoints and WebSocket for real-time updates.
NOW PROPERLY CONNECTED TO AUTONOMOUS EXECUTOR!
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.config import context_settings, LM_STUDIO_URL, WORKSPACE_DIR
from agents.orchestrator import orchestrator
from agents.recycler import recycler
from agents.autonomous import autonomous_executor  # THE REAL AUTONOMOUS ENGINE!

app = FastAPI(title="Jarvis API", version="2.0")

# Thread pool for running sync code in async context
executor = ThreadPoolExecutor(max_workers=2)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections for live updates
active_connections: List[WebSocket] = []


class ChatMessage(BaseModel):
    message: str
    autonomous: bool = False


class SettingsUpdate(BaseModel):
    max_tokens: Optional[int] = None
    recycle_threshold: Optional[float] = None
    model_name: Optional[str] = None


# --- WebSocket Manager ---
async def broadcast_log(message: str, msg_type: str = "log"):
    """Send log message to all connected clients."""
    for connection in active_connections:
        try:
            await connection.send_json({"type": msg_type, "content": message})
        except:
            pass


async def broadcast_progress(message: str):
    """Send progress update to all connected clients."""
    for connection in active_connections:
        try:
            await connection.send_json({
                "type": "progress",
                "content": message
            })
        except:
            pass


def sync_progress_callback(message: str):
    """Sync callback that schedules async broadcast."""
    # Get or create event loop for this thread
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_progress(message))
        else:
            loop.run_until_complete(broadcast_progress(message))
    except RuntimeError:
        # No event loop in this thread, create one
        loop = asyncio.new_event_loop()
        loop.run_until_complete(broadcast_progress(message))


# --- REST Endpoints ---
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "llm_url": LM_STUDIO_URL}


@app.get("/api/settings")
async def get_settings():
    """Get current context settings."""
    return {
        **context_settings.to_dict(),
        "context_usage": recycler.get_context_usage()
    }


@app.post("/api/settings")
async def update_settings(settings: SettingsUpdate):
    """Update context settings at runtime."""
    context_settings.update(**settings.dict(exclude_none=True))
    # Also update recycler
    if settings.max_tokens:
        recycler.max_tokens = settings.max_tokens
    if settings.recycle_threshold:
        recycler.threshold = settings.recycle_threshold
    return {"status": "updated", "settings": context_settings.to_dict()}


@app.post("/api/chat")
async def chat(msg: ChatMessage):
    """Process a chat message."""
    try:
        if msg.autonomous:
            # Run autonomous executor in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: autonomous_executor.run(msg.message, progress_callback=sync_progress_callback)
            )
        else:
            # Regular orchestrator for quick tasks
            result = orchestrator.execute(msg.message, callback=None)
        
        # Format response
        if isinstance(result, dict):
            response = result.get("result", result.get("summary", str(result)))
        else:
            response = str(result)
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/projects")
async def list_projects():
    """List all projects in workspace."""
    projects_dir = os.path.join(WORKSPACE_DIR, "projects")
    if not os.path.exists(projects_dir):
        return {"projects": []}
    
    projects = []
    for name in os.listdir(projects_dir):
        path = os.path.join(projects_dir, name)
        if os.path.isdir(path):
            file_count = sum(len(files) for _, _, files in os.walk(path))
            projects.append({
                "name": name,
                "path": path,
                "file_count": file_count
            })
    
    return {"projects": projects}


@app.get("/api/autonomous/status")
async def autonomous_status():
    """Get current autonomous execution status."""
    return {
        "is_running": autonomous_executor.is_running,
        "is_paused": autonomous_executor.is_paused,
        "current_task": autonomous_executor.current_task,
        "iteration": autonomous_executor.iteration,
        "log_count": len(autonomous_executor.log)
    }


@app.post("/api/autonomous/pause")
async def autonomous_pause():
    """Pause autonomous execution."""
    result = autonomous_executor.pause()
    return result


@app.post("/api/autonomous/resume")
async def autonomous_resume():
    """Resume autonomous execution."""
    result = autonomous_executor.resume()
    return result


@app.post("/api/autonomous/stop")
async def autonomous_stop():
    """Stop autonomous execution."""
    autonomous_executor.stop()
    return {"status": "stopped"}


# === CHECKPOINT MANAGEMENT ===
@app.get("/api/checkpoints")
async def list_checkpoints():
    """List all available checkpoints for resume."""
    from agents.utils.checkpoint import checkpoint_manager
    checkpoints = checkpoint_manager.list_checkpoints()
    return {"checkpoints": checkpoints}


@app.get("/api/checkpoints/{checkpoint_id}")
async def get_checkpoint(checkpoint_id: str):
    """Get details of a specific checkpoint."""
    from agents.utils.checkpoint import checkpoint_manager
    cp = checkpoint_manager.get_checkpoint_by_id(checkpoint_id)
    if cp:
        return cp
    return {"error": "Checkpoint not found"}


@app.post("/api/autonomous/resume/{checkpoint_id}")
async def resume_from_checkpoint(checkpoint_id: str):
    """Resume autonomous execution from a saved checkpoint."""
    from agents.utils.checkpoint import checkpoint_manager
    
    # Verify checkpoint exists
    cp = checkpoint_manager.get_checkpoint_by_id(checkpoint_id)
    if not cp:
        return {"error": f"Checkpoint {checkpoint_id} not found"}
    
    # Run in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        lambda: autonomous_executor.run("", resume_checkpoint=checkpoint_id)
    )
    
    return {
        "status": "completed",
        "resumed_from": checkpoint_id,
        "result": result
    }


@app.delete("/api/checkpoints/{checkpoint_id}")
async def delete_checkpoint(checkpoint_id: str):
    """Delete a specific checkpoint."""
    from agents.utils.checkpoint import checkpoint_manager
    success = checkpoint_manager.delete_checkpoint(checkpoint_id)
    return {"deleted": success}


# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "chat":
                message = data.get("message", "")
                autonomous = data.get("autonomous", False)
                resume_checkpoint = data.get("resume_checkpoint", None)  # NEW: Resume support
                
                # Send acknowledgment
                await websocket.send_json({"type": "ack", "message": "Processing..."})
                
                # Process in background
                async def process():
                    try:
                        if autonomous:
                            # AUTONOMOUS MODE: Use the real autonomous executor!
                            if resume_checkpoint:
                                await websocket.send_json({
                                    "type": "progress",
                                    "content": f"🔄 Resuming from checkpoint {resume_checkpoint}..."
                                })
                            else:
                                await websocket.send_json({
                                    "type": "progress",
                                    "content": "🚀 Starting Autonomous Execution..."
                                })
                            
                            def progress_callback(msg):
                                # Schedule broadcast in the main loop
                                asyncio.create_task(broadcast_progress(msg))
                            
                            # Run in thread pool (autonomous is blocking)
                            loop = asyncio.get_event_loop()
                            result = await loop.run_in_executor(
                                executor,
                                lambda: autonomous_executor.run(
                                    message, 
                                    progress_callback=progress_callback,
                                    resume_checkpoint=resume_checkpoint  # NEW: Pass checkpoint
                                )
                            )
                        else:
                            # Regular chat mode
                            def callback(log_msg):
                                asyncio.create_task(broadcast_log(log_msg))
                            
                            result = orchestrator.execute(message, callback=callback)
                        
                        # Format response
                        if isinstance(result, dict):
                            response = result.get("result", result.get("summary", str(result)))
                        else:
                            response = str(result)
                        
                        await websocket.send_json({"type": "response", "content": response})
                    except Exception as e:
                        await websocket.send_json({"type": "error", "content": str(e)})
                
                asyncio.create_task(process())
                
            elif data.get("type") == "get_status":
                await websocket.send_json({
                    "type": "status",
                    "settings": context_settings.to_dict(),
                    "context_usage": recycler.get_context_usage(),
                    "autonomous": {
                        "is_running": autonomous_executor.is_running,
                        "is_paused": autonomous_executor.is_paused
                    }
                })
            
            elif data.get("type") == "pause":
                result = autonomous_executor.pause()
                await websocket.send_json({"type": "pause_result", "result": result})
            
            elif data.get("type") == "resume":
                result = autonomous_executor.resume()
                await websocket.send_json({"type": "resume_result", "result": result})
            
            elif data.get("type") == "stop":
                autonomous_executor.stop()
                await websocket.send_json({"type": "stopped"})
                
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)


# --- Static Files (React frontend) ---
# Serve static files from frontend/dist after build
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
