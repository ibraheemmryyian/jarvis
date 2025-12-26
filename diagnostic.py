"""
Jarvis Pre-Flight Diagnostic
Run this before a stress test to ensure all systems are ready.
"""
import os
import sys

# Colors for terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check(name: str, condition: bool, fix: str = ""):
    if condition:
        print(f"{GREEN}✓{RESET} {name}")
        return True
    else:
        print(f"{RED}✗{RESET} {name}")
        if fix:
            print(f"  {YELLOW}→ Fix: {fix}{RESET}")
        return False

def main():
    print("\n" + "="*50)
    print("  JARVIS PRE-FLIGHT DIAGNOSTIC")
    print("="*50 + "\n")
    
    all_passed = True
    
    # 1. Check imports
    print("[1] Core Imports")
    try:
        from agents import autonomous_executor
        check("autonomous_executor", True)
    except Exception as e:
        check("autonomous_executor", False, str(e))
        all_passed = False
    
    try:
        from agents import orchestrator
        check("orchestrator", True)
    except Exception as e:
        check("orchestrator", False, str(e))
        all_passed = False
    
    try:
        from agents.recycler import recycler
        check("recycler", True)
    except Exception as e:
        check("recycler", False, str(e))
        all_passed = False
    
    try:
        from agents.config import context_settings
        check("context_settings", True)
    except Exception as e:
        check("context_settings", False, str(e))
        all_passed = False
    
    # 2. Check specialists
    print("\n[2] Specialist Agents")
    specialists = [
        ("frontend_dev", "from agents.frontend_dev import frontend_dev"),
        ("backend_dev", "from agents.backend_dev import backend_dev"),
        ("brute_researcher", "from agents.brute_research import brute_researcher"),
        ("content_writer", "from agents.content_writer import content_writer"),
        ("coder", "from agents.coder import coder"),
        ("ops", "from agents.ops import ops"),
    ]
    
    for name, import_stmt in specialists:
        try:
            exec(import_stmt)
            # Check if run() method exists
            agent = eval(name.replace("brute_researcher", "brute_researcher"))
            if hasattr(agent, 'run'):
                check(f"{name}.run()", True)
            else:
                check(f"{name}.run()", False, "Missing run() method")
                all_passed = False
        except Exception as e:
            check(name, False, str(e))
            all_passed = False
    
    # 3. Check LM Studio connection
    print("\n[3] LLM Connection")
    try:
        import requests
        from agents.config import LM_STUDIO_URL
        
        # Try to hit the models endpoint
        base_url = LM_STUDIO_URL.replace("/chat/completions", "/models")
        resp = requests.get(base_url, timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("data", [])
            if models:
                model_name = models[0].get("id", "unknown")
                check(f"LM Studio ({model_name})", True)
            else:
                check("LM Studio", False, "No models loaded")
                all_passed = False
        else:
            check("LM Studio", False, f"Status {resp.status_code}")
            all_passed = False
    except Exception as e:
        check("LM Studio", False, f"Not running? {e}")
        all_passed = False
    
    # 4. Check config
    print("\n[4] Configuration")
    try:
        from agents.config import context_settings, MAX_CONTEXT_TOKENS
        
        check(f"max_tokens: {context_settings.max_tokens}", context_settings.max_tokens >= 4096)
        check(f"recycle_threshold: {context_settings.recycle_threshold}", 0.5 <= context_settings.recycle_threshold <= 0.95)
    except Exception as e:
        check("Configuration", False, str(e))
        all_passed = False
    
    # 5. Check workspace
    print("\n[5] Workspace")
    from agents.config import WORKSPACE_DIR, CONTEXT_DIR
    
    check(f"WORKSPACE_DIR exists", os.path.exists(WORKSPACE_DIR))
    check(f"CONTEXT_DIR exists", os.path.exists(CONTEXT_DIR))
    
    # 6. Check key files
    print("\n[6] Key Files")
    key_files = [
        "agents/autonomous.py",
        "agents/frontend_dev.py",
        "agents/backend_dev.py",
        "agents/config.py",
        "agents/recycler.py",
    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for f in key_files:
        path = os.path.join(base_dir, f)
        check(f, os.path.exists(path))
    
    # Summary
    print("\n" + "="*50)
    if all_passed:
        print(f"{GREEN}  ALL CHECKS PASSED - READY FOR LAUNCH{RESET}")
    else:
        print(f"{RED}  SOME CHECKS FAILED - FIX ISSUES ABOVE{RESET}")
    print("="*50 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
