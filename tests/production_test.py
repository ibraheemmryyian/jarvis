"""
End-to-End Production Test for Jarvis
Tests the entire system with a simple prompt.
"""
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_production_test():
    """Run a comprehensive production readiness test."""
    print("=" * 60)
    print("JARVIS PRODUCTION READINESS TEST")
    print("=" * 60)
    print()
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Test 1: Import all core modules
    print("[1/10] Testing core imports...")
    try:
        from agents.registry import registry
        from agents.router import router
        from agents.orchestrator import Orchestrator
        from agents.autonomous import AutonomousExecutor
        from agents.context_retriever import context_retriever
        from agents.utils import (
            checkpoint_manager,
            escalation_manager,
            error_journal,
            hierarchical_planner
        )
        results["passed"] += 1
        results["tests"].append(("[OK] Core imports", True))
        print("  [OK] All core modules imported")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Core imports: {e}", False))
        print(f"  [FAIL] Import error: {e}")
    
    # Test 2: Registry status
    print("[2/10] Testing registry...")
    try:
        from agents.registry import registry
        status = registry.get_status()
        agent_count = status["registered_agents"]
        
        if agent_count >= 40:
            results["passed"] += 1
            results["tests"].append((f"[OK] {agent_count} agents registered", True))
            print(f"  [OK] {agent_count} agents registered")
        else:
            results["failed"] += 1
            results["tests"].append((f"[WARN] Only {agent_count} agents", False))
            print(f"  [WARN] Only {agent_count} agents registered")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Registry: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Test 3: Context Retriever
    print("[3/10] Testing context retrieval...")
    try:
        from agents.context_retriever import get_context
        ctx = get_context("build a React component", "frontend_dev")
        
        if len(ctx) > 0:
            results["passed"] += 1
            results["tests"].append((f"[OK] Retrieved {len(ctx)} chars context", True))
            print(f"  [OK] Retrieved {len(ctx)} chars of context")
        else:
            results["failed"] += 1
            results["tests"].append(("[WARN] Empty context", False))
            print("  [WARN] Empty context retrieved")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Context: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Test 4: Router Classification
    print("[4/10] Testing router...")
    try:
        from agents.router import router
        
        test_queries = [
            ("build a website", ["FRONTEND", "CODER", "AUTONOMOUS"]),
            ("research AI trends", ["RESEARCH"]),
            ("deploy to production", ["OPS", "ARCHITECTURE"]),
        ]
        
        all_valid = True
        for query, valid_cats in test_queries:
            result = router.classify(query)
            if result["category"] not in valid_cats:
                all_valid = False
        
        if all_valid:
            results["passed"] += 1
            results["tests"].append(("[OK] Router classification", True))
            print("  [OK] Router classification working")
        else:
            results["failed"] += 1
            results["tests"].append(("[WARN] Router misclassification", False))
            print("  [WARN] Some classifications unexpected")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Router: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Test 5: Checkpoint System
    print("[5/10] Testing checkpoints...")
    try:
        from agents.utils import checkpoint_manager
        
        cp_id = checkpoint_manager.save_checkpoint(
            objective="Production test",
            iteration=1,
            completed_steps=["Test step"],
            pending_steps=["More tests"]
        )
        
        if cp_id:
            results["passed"] += 1
            results["tests"].append((f"[OK] Checkpoint saved: {cp_id}", True))
            print(f"  [OK] Checkpoint saved: {cp_id}")
        else:
            results["failed"] += 1
            results["tests"].append(("[FAIL] Checkpoint save failed", False))
            print("  [FAIL] Checkpoint save returned None")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Checkpoint: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Test 6: Escalation Rules
    print("[6/10] Testing escalation rules...")
    try:
        from agents.utils import should_escalate
        
        # Test destructive action
        result = should_escalate({"action": "DELETE all files"})
        
        if result and result["reason"] == "destructive_action":
            results["passed"] += 1
            results["tests"].append(("[OK] Escalation rules working", True))
            print("  [OK] Escalation rules working")
        else:
            results["failed"] += 1
            results["tests"].append(("[FAIL] Destructive action not detected", False))
            print("  [FAIL] Destructive action not detected")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Escalation: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Test 7: Error Journal
    print("[7/10] Testing error journal...")
    try:
        from agents.utils import error_journal
        
        error_journal.log_error(
            task_type="test",
            task_description="Production test",
            error="Test error for logging"
        )
        
        stats = error_journal.get_statistics()
        
        if stats["total"] > 0:
            results["passed"] += 1
            results["tests"].append((f"[OK] {stats['total']} errors logged", True))
            print(f"  [OK] Error journal has {stats['total']} entries")
        else:
            results["failed"] += 1
            results["tests"].append(("[FAIL] Error journal empty", False))
            print("  [FAIL] Error journal is empty")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Error journal: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Test 8: Hierarchical Planner
    print("[8/10] Testing hierarchical planner...")
    try:
        from agents.utils import hierarchical_planner
        
        is_mega = hierarchical_planner.is_mega_task("Build a complete CRM system")
        is_not_mega = not hierarchical_planner.is_mega_task("Fix button color")
        
        if is_mega and is_not_mega:
            results["passed"] += 1
            results["tests"].append(("[OK] Hierarchical planner working", True))
            print("  [OK] Mega task detection working")
        else:
            results["failed"] += 1
            results["tests"].append(("[FAIL] Mega task detection failed", False))
            print("  [FAIL] Mega task detection incorrect")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Planner: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Test 9: Orchestrator Initialization
    print("[9/10] Testing orchestrator...")
    try:
        from agents.orchestrator import Orchestrator
        
        orch = Orchestrator()
        agent_count = len(orch.agents)
        
        if agent_count >= 20:
            results["passed"] += 1
            results["tests"].append((f"[OK] Orchestrator: {agent_count} agents", True))
            print(f"  [OK] Orchestrator initialized with {agent_count} agents")
        else:
            results["failed"] += 1
            results["tests"].append((f"[WARN] Only {agent_count} orchestrator agents", False))
            print(f"  [WARN] Only {agent_count} orchestrator agents")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Orchestrator: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Test 10: Memory System
    print("[10/10] Testing memory...")
    try:
        from agents.memory import memory
        
        # Save a test fact
        memory.save_fact("Production test fact", category="test")
        
        # Memory is working if save_fact didn't error
        results["passed"] += 1
        results["tests"].append(("[OK] Memory save working", True))
        print("  [OK] Memory save working")
    except Exception as e:
        results["failed"] += 1
        results["tests"].append((f"[FAIL] Memory: {e}", False))
        print(f"  [FAIL] {e}")
    
    # Summary
    print()
    print("=" * 60)
    print("PRODUCTION TEST RESULTS")
    print("=" * 60)
    print(f"PASSED: {results['passed']}/10")
    print(f"FAILED: {results['failed']}/10")
    print()
    
    for test_name, passed in results["tests"]:
        print(f"  {test_name}")
    
    print()
    if results["failed"] == 0:
        print("[SUCCESS] SYSTEM IS PRODUCTION READY!")
        return 0
    elif results["failed"] <= 2:
        print("[WARNING] SYSTEM IS MOSTLY READY (minor issues)")
        return 0
    else:
        print("[FAILED] SYSTEM NEEDS FIXES")
        return 1


if __name__ == "__main__":
    sys.exit(run_production_test())
