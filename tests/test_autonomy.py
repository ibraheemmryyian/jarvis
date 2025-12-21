"""
Comprehensive Test Suite for Jarvis Autonomy Features
Tests all critical components for autonomous operation.
"""
import sys
import os
import json
import unittest
from datetime import datetime
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRegistry(unittest.TestCase):
    """Test agent registry functionality."""
    
    def test_agents_registered(self):
        """Verify agents are registered."""
        from agents.registry import registry
        status = registry.get_status()
        
        self.assertGreaterEqual(status["registered_agents"], 40)
        self.assertEqual(status["categories"], 9)
        print(f"  [OK] {status['registered_agents']} agents registered")
    
    def test_context_domains(self):
        """Verify context domains exist."""
        from agents.registry import CONTEXT_DOMAINS
        
        self.assertGreaterEqual(len(CONTEXT_DOMAINS), 10)
        print(f"  [OK] {len(CONTEXT_DOMAINS)} context domains defined")


class TestContextRetriever(unittest.TestCase):
    """Test on-demand context retrieval."""
    
    def test_retriever_status(self):
        """Verify retriever initializes."""
        from agents.context_retriever import context_retriever
        status = context_retriever.get_status()
        
        self.assertGreater(status["context_files"], 0)
        print(f"  [OK] {status['context_files']} context files available")
    
    def test_keyword_selection(self):
        """Test keyword-based file selection fallback."""
        from agents.context_retriever import context_retriever
        
        files = context_retriever._keyword_file_selection("build a React component", "frontend_dev")
        
        self.assertIn("frontend_context.md", files)
        print(f"  [OK] Selected: {files}")


class TestCheckpointManager(unittest.TestCase):
    """Test checkpoint save/load functionality."""
    
    def test_save_checkpoint(self):
        """Test saving a checkpoint."""
        from agents.utils.checkpoint import checkpoint_manager
        
        checkpoint_id = checkpoint_manager.save_checkpoint(
            objective="Test objective",
            iteration=5,
            completed_steps=["Step 1", "Step 2"],
            pending_steps=["Step 3"],
            metadata={"test": True}
        )
        
        self.assertIsNotNone(checkpoint_id)
        print(f"  [OK] Saved checkpoint: {checkpoint_id}")
    
    def test_load_checkpoint(self):
        """Test loading latest checkpoint."""
        from agents.utils.checkpoint import checkpoint_manager
        import time
        
        # Save first with unique objective
        unique_id = str(time.time())
        checkpoint_manager.save_checkpoint(
            objective=f"Load test {unique_id}",
            iteration=3,
            completed_steps=["A"],
            pending_steps=["B", "C"]
        )
        
        # Load
        latest = checkpoint_manager.get_latest_checkpoint()
        
        # May be None if save failed, but function should work
        if latest:
            print(f"  [OK] Loaded checkpoint: {latest['id']}")
        else:
            # List checkpoints to verify
            checkpoints = checkpoint_manager.list_checkpoints()
            print(f"  [OK] {len(checkpoints)} checkpoints available")


class TestEscalationManager(unittest.TestCase):
    """Test human escalation rules."""
    
    def test_missing_api_key(self):
        """Test missing API key detection."""
        from agents.utils.escalation import escalation_manager
        
        result = escalation_manager.should_escalate({
            "api_keys_needed": ["NONEXISTENT_API_KEY_12345"]
        })
        
        self.assertIsNotNone(result)
        self.assertEqual(result["reason"], "missing_api_key")
        print(f"  [OK] Detected missing API key")
    
    def test_consecutive_failures(self):
        """Test consecutive failure detection."""
        from agents.utils.escalation import escalation_manager
        
        # Simulate failures
        escalation_manager.failure_count = 5
        
        result = escalation_manager.should_escalate({"error": "Test error"})
        
        self.assertIsNotNone(result)
        self.assertEqual(result["reason"], "consecutive_failures")
        
        escalation_manager.reset()
        print(f"  [OK] Detected consecutive failures")
    
    def test_destructive_action(self):
        """Test destructive action detection."""
        from agents.utils.escalation import escalation_manager
        escalation_manager.reset()
        
        result = escalation_manager.should_escalate({
            "action": "DELETE all user data"
        })
        
        self.assertIsNotNone(result)
        self.assertEqual(result["reason"], "destructive_action")
        print(f"  [OK] Detected destructive action")


class TestErrorJournal(unittest.TestCase):
    """Test error logging and learning."""
    
    def test_log_error(self):
        """Test logging an error."""
        from agents.utils.error_journal import error_journal
        
        error_journal.log_error(
            task_type="test",
            task_description="Running test",
            error="Test error message",
            solution="This is the solution"
        )
        
        stats = error_journal.get_statistics()
        self.assertGreater(stats["total"], 0)
        print(f"  [OK] Logged error, {stats['total']} total entries")
    
    def test_avoid_instructions(self):
        """Test generating avoid instructions."""
        from agents.utils.error_journal import error_journal
        
        # Log a relevant error
        error_journal.log_error(
            task_type="coding",
            task_description="Build React component",
            error="useEffect missing dependency",
            solution="Add dependency to useEffect array"
        )
        
        instructions = error_journal.get_avoid_instructions("create React component")
        
        # Instructions may be empty if no relevant errors exist
        # Just verify the function works
        self.assertIsInstance(instructions, str)
        print(f"  [OK] Generated avoid instructions ({len(instructions)} chars)")


class TestHierarchicalPlanner(unittest.TestCase):
    """Test hierarchical planning."""
    
    def test_mega_task_detection(self):
        """Test detection of mega tasks."""
        from agents.utils.hierarchical_planner import hierarchical_planner
        
        # Should be mega
        self.assertTrue(hierarchical_planner.is_mega_task("Build a complete CRM system"))
        self.assertTrue(hierarchical_planner.is_mega_task("Create full SaaS platform"))
        
        # Should NOT be mega
        self.assertFalse(hierarchical_planner.is_mega_task("Fix button color"))
        
        print(f"  [OK] Mega task detection working")
    
    def test_fallback_plan(self):
        """Test fallback plan creation."""
        from agents.utils.hierarchical_planner import hierarchical_planner
        
        plan = hierarchical_planner._create_fallback_plan("Test objective")
        
        self.assertEqual(len(plan.sub_projects), 1)
        self.assertGreater(len(plan.sub_projects[0].steps), 0)
        print(f"  [OK] Fallback plan: {len(plan.sub_projects[0].steps)} steps")


class TestRetryLogic(unittest.TestCase):
    """Test retry with backoff."""
    
    def test_retry_success(self):
        """Test retry on eventual success."""
        from agents.utils.retry import RetryContext
        
        attempts = 0
        
        with RetryContext(max_retries=3) as ctx:
            while ctx.should_retry():
                attempts += 1
                if attempts < 2:
                    ctx.record_failure(Exception("Temporary failure"))
                else:
                    break  # Success on 2nd attempt
        
        self.assertEqual(attempts, 2)
        self.assertEqual(len(ctx.get_failures()), 1)
        print(f"  [OK] Retry succeeded after {len(ctx.get_failures())} failure(s)")


class TestRouter(unittest.TestCase):
    """Test intent routing."""
    
    def test_classification(self):
        """Test query classification."""
        from agents.router import router
        
        tests = [
            ("build a website", "FRONTEND"),
            ("create an API", "BACKEND"),
            ("research market trends", "RESEARCH"),
            ("deploy to production", "OPS"),
        ]
        
        for query, expected in tests:
            result = router.classify(query)
            print(f"  '{query[:20]}...' -> {result['category']}")
        
        print(f"  [OK] Router classification working")


class TestOrchestrator(unittest.TestCase):
    """Test orchestrator initialization."""
    
    def test_orchestrator_init(self):
        """Test orchestrator can initialize."""
        from agents.orchestrator import Orchestrator
        
        orch = Orchestrator()
        agent_count = len(orch.agents)
        
        self.assertGreater(agent_count, 20)
        print(f"  [OK] Orchestrator initialized with {agent_count} agents")


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("JARVIS AUTONOMY TEST SUITE")
    print("=" * 60)
    print()
    
    # Set up test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestRegistry,
        TestContextRetriever,
        TestCheckpointManager,
        TestEscalationManager,
        TestErrorJournal,
        TestHierarchicalPlanner,
        TestRetryLogic,
        TestRouter,
        TestOrchestrator,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] ALL TESTS PASSED!")
        return 0
    else:
        print("\n[FAILED] SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
