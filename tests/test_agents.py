"""
Jarvis v2 Automated Test Suite
Tests all agents with real LLM calls.
"""
import sys
import os
import time
import json

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import (
    router, 
    deep_research_v2, 
    coder, 
    orchestrator,
    queue_autonomous,
    start_queue_worker,
    get_queue_status,
    context
)

RESULTS = {
    "tests_run": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "details": []
}


def log_result(test_name: str, passed: bool, message: str = "", data: any = None):
    """Log a test result."""
    RESULTS["tests_run"] += 1
    if passed:
        RESULTS["tests_passed"] += 1
        status = "[PASS]"
    else:
        RESULTS["tests_failed"] += 1
        status = "[FAIL]"
    
    print(f"\n{status}: {test_name}")
    if message:
        print(f"   -> {message}")
    
    RESULTS["details"].append({
        "test": test_name,
        "passed": passed,
        "message": message,
        "data": str(data)[:200] if data else None
    })


def test_router():
    """Test router intent classification."""
    print("\n" + "="*50)
    print("TEST: Router Agent")
    print("="*50)
    
    test_cases = [
        ("hello how are you", "CHAT"),
        ("research PDF editing tools", "RESEARCH"),
        ("build me a calculator app", "CODER"),
        ("deploy to github", "OPS"),
        ("I want to create a SaaS for invoice management", "AUTONOMOUS"),
    ]
    
    for query, expected in test_cases:
        try:
            result = router.classify(query)
            actual = result.get("agent", "UNKNOWN")
            passed = actual == expected
            log_result(
                f"Router: '{query[:30]}...'",
                passed,
                f"Expected {expected}, got {actual}",
                result
            )
        except Exception as e:
            log_result(f"Router: '{query[:30]}...'", False, str(e))


def test_brute_research():
    """Test brute force research (quick version - fewer sources)."""
    print("\n" + "="*50)
    print("TEST: Brute Force Research")
    print("="*50)
    
    try:
        from agents.brute_research import brute_researcher
        
        # Quick test with limited sources
        results = brute_researcher.gather("PDF tools")
        
        log_result(
            "Brute Research: Gather",
            len(results) > 5,
            f"Gathered {len(results)} results from sources",
            {"count": len(results)}
        )
        
        # Test aggregation
        aggregated = brute_researcher.aggregate_by_category()
        log_result(
            "Brute Research: Aggregation",
            len(aggregated) > 0,
            f"Categories: {list(aggregated.keys())}",
            aggregated
        )
        
        # Test context string
        context_str = brute_researcher.to_context_string()
        log_result(
            "Brute Research: Context String",
            len(context_str) > 100,
            f"Context length: {len(context_str)} chars"
        )
        
    except Exception as e:
        log_result("Brute Research", False, str(e))


def test_synthesis():
    """Test research synthesis with LLM."""
    print("\n" + "="*50)
    print("TEST: Synthesis Engine (LLM)")
    print("="*50)
    
    try:
        from agents.synthesis import synthesizer
        from agents.brute_research import brute_researcher
        
        # Get raw context from previous test
        raw_context = brute_researcher.to_context_string()
        
        if len(raw_context) > 100:
            # Synthesize (this calls the LLM)
            report = synthesizer.synthesize("PDF tools", raw_context[:4000])
            
            log_result(
                "Synthesis: Report Generation",
                len(report) > 200 and "GO" in report.upper(),
                f"Report length: {len(report)} chars",
                report[:300]
            )
        else:
            log_result("Synthesis: Report Generation", False, "Not enough research data")
            
    except Exception as e:
        log_result("Synthesis", False, str(e))


def test_coder():
    """Test coder agent."""
    print("\n" + "="*50)
    print("TEST: Coder Agent")
    print("="*50)
    
    try:
        result = coder.run("Create a simple hello world Python script")
        
        log_result(
            "Coder: Code Generation",
            result is not None,
            f"Generated output: {str(result)[:100]}...",
            result
        )
        
    except Exception as e:
        log_result("Coder", False, str(e))


def test_queue():
    """Test queue system."""
    print("\n" + "="*50)
    print("TEST: Queue System")
    print("="*50)
    
    try:
        # Get initial status
        status = get_queue_status()
        log_result(
            "Queue: Status Check",
            "pending" in status,
            f"Status: {status}"
        )
        
        # Add a task (don't execute)
        from agents.queue import task_queue, TaskType
        task_id = task_queue.add(TaskType.RESEARCH, {"topic": "test topic"})
        
        log_result(
            "Queue: Add Task",
            task_id > 0,
            f"Task ID: {task_id}"
        )
        
        # Check pending count
        pending = task_queue.get_pending_count()
        log_result(
            "Queue: Pending Count",
            pending > 0,
            f"Pending: {pending}"
        )
        
    except Exception as e:
        log_result("Queue", False, str(e))


def test_context_manager():
    """Test context manager."""
    print("\n" + "="*50)
    print("TEST: Context Manager")
    print("="*50)
    
    try:
        # Set active task
        context.set_active_task("Test task", ["subtask 1", "subtask 2"])
        
        # Read it back
        task = context.read_active_task()
        log_result(
            "Context: Active Task",
            "Test task" in task,
            f"Task content length: {len(task)}"
        )
        
        # Log a decision
        context.log_decision("Test decision", "Test reasoning")
        decisions = context.read_context("decisions")
        log_result(
            "Context: Decisions",
            "Test decision" in decisions,
            "Decision logged successfully"
        )
        
    except Exception as e:
        log_result("Context Manager", False, str(e))


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("JARVIS V2 AUTOMATED TEST SUITE")
    print("="*60)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_context_manager()
    test_router()
    test_brute_research()
    test_synthesis()
    test_coder()
    test_queue()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {RESULTS['tests_run']}")
    print(f"Passed:      {RESULTS['tests_passed']} ✅")
    print(f"Failed:      {RESULTS['tests_failed']} ❌")
    print(f"Pass Rate:   {RESULTS['tests_passed']/max(1, RESULTS['tests_run'])*100:.1f}%")
    
    # Save results
    results_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "test_results.json"
    )
    with open(results_path, "w") as f:
        json.dump(RESULTS, f, indent=2)
    print(f"\nResults saved to: {results_path}")
    
    return RESULTS


if __name__ == "__main__":
    run_all_tests()
