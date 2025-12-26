"""
Jarvis Web UI Launcher
Starts both the FastAPI backend and React frontend dev server.
"""
import os
import sys
import subprocess
import time
import webbrowser

# Paths
UI_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(UI_DIR, "frontend")
JARVIS_DIR = os.path.dirname(UI_DIR)

# Add jarvis to path
sys.path.insert(0, JARVIS_DIR)


def check_node():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def install_frontend_deps():
    """Install frontend dependencies if needed."""
    node_modules = os.path.join(FRONTEND_DIR, "node_modules")
    if not os.path.exists(node_modules):
        print("[UI] Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, shell=True)


def main():
    print("=" * 50)
    print("    J.A.R.V.I.S Web UI Launcher")
    print("=" * 50)
    
    # Check Node.js
    if not check_node():
        print("[ERROR] Node.js not found. Please install Node.js first.")
        print("        https://nodejs.org/")
        return
    
    # Install deps
    install_frontend_deps()
    
    # Start backend
    print("[UI] Starting backend server on http://127.0.0.1:8000")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=UI_DIR
    )
    
    time.sleep(2)  # Wait for backend to start
    
    # Start frontend dev server
    print("[UI] Starting frontend on http://127.0.0.1:5173")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True
    )
    
    time.sleep(3)
    
    # Open browser
    print("[UI] Opening browser...")
    webbrowser.open("http://127.0.0.1:5173")
    
    print("\n" + "=" * 50)
    print("    Jarvis UI is running!")
    print("    Frontend: http://127.0.0.1:5173")
    print("    Backend:  http://127.0.0.1:8000")
    print("    Press Ctrl+C to stop")
    print("=" * 50 + "\n")
    
    try:
        # Keep running until Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[UI] Shutting down...")
        frontend_proc.terminate()
        backend_proc.terminate()
        print("[UI] Goodbye!")


if __name__ == "__main__":
    main()
