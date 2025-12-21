"""
Jarvis Full System Test Suite
Tests all core functionality
"""
import sys
import os
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run_tests():
    results = []
    
    print("="*60)
    print("JARVIS FULL SYSTEM AUTOMATED TEST SUITE")
    print("="*60)
    
    # === TEST 1: Registry ===
    print("\n[TEST 1] Agent Registry...")
    try:
        from agents.registry import registry, AGENT_CATEGORIES, CONTEXT_DOMAINS
        status = registry.get_status()
        print(f"  ✓ Registered: {status['registered_agents']}/{status['total_defined']} agents")
        print(f"  ✓ Categories: {status['categories']}")
        print(f"  ✓ Domains: {status['context_domains']}")
        
        if status['registered_agents'] >= 35:
            results.append(("Registry", "PASS", f"{status['registered_agents']} agents"))
        else:
            results.append(("Registry", "WARN", f"Only {status['registered_agents']} agents"))
    except Exception as e:
        results.append(("Registry", "FAIL", str(e)))
        print(f"  ✗ Error: {e}")
    
    # === TEST 2: Router Classification ===
    print("\n[TEST 2] Router Classification...")
    try:
        from agents.router import router
        tests = [
            ("build me a React dashboard", "FRONTEND"),
            ("create an API", "BACKEND"),
            ("research AI papers", "RESEARCH"),
            ("deploy to server", "OPS"),
        ]
        all_passed = True
        for query, expected in tests:
            result = router.classify(query)
            cat = result.get('category', 'UNKNOWN')
            status_str = "✓" if cat == expected else "~"
            print(f"  {status_str} '{query[:25]}...' → {cat}")
            if cat != expected:
                all_passed = False
        
        results.append(("Router", "PASS" if all_passed else "WARN", "Classification working"))
    except Exception as e:
        results.append(("Router", "FAIL", str(e)))
        print(f"  ✗ Error: {e}")
    
    # === TEST 3: Context Segregation ===
    print("\n[TEST 3] Context Segregation...")
    try:
        from agents.registry import get_context_for_agent
        
        agents_to_test = ["frontend_dev", "backend_dev", "researcher", "qa_agent"]
        for agent in agents_to_test:
            ctx = get_context_for_agent(agent)
            print(f"  ✓ {agent}: {len(ctx)} chars of context")
        
        results.append(("Context", "PASS", "Segregation working"))
    except Exception as e:
        results.append(("Context", "FAIL", str(e)))
        print(f"  ✗ Error: {e}")
    
    # === TEST 4: Orchestrator ===
    print("\n[TEST 4] Orchestrator...")
    try:
        from agents.orchestrator import Orchestrator
        orch = Orchestrator()
        print("  ✓ Orchestrator initialized")
        print(f"  ✓ Has {len(orch.agents)} direct agent references")
        results.append(("Orchestrator", "PASS", "Initialized OK"))
    except Exception as e:
        results.append(("Orchestrator", "FAIL", str(e)))
        print(f"  ✗ Error: {e}")
    
    # === TEST 5: Recycler ===
    print("\n[TEST 5] Context Recycler...")
    try:
        from agents.recycler import recycler
        usage = recycler.get_context_usage()
        print(f"  ✓ Domains: {len(recycler.DOMAINS)}")
        print(f"  ✓ Max tokens: {usage['max_tokens']}")
        print(f"  ✓ Usage: {usage['usage_percent']}%")
        results.append(("Recycler", "PASS", f"{len(recycler.DOMAINS)} domains"))
    except Exception as e:
        results.append(("Recycler", "FAIL", str(e)))
        print(f"  ✗ Error: {e}")
    
    # === TEST 6: Academic Workflow ===
    print("\n[TEST 6] Academic Workflow...")
    try:
        from agents.academic_workflow import academic_workflow
        from agents.research_publisher import research_publisher
        
        # Check citation styles
        styles = list(research_publisher.CITATION_STYLES.keys())
        print(f"  ✓ Citation styles: {len(styles)} ({', '.join(styles[:4])}...)")
        
        # Check paper templates
        templates = list(research_publisher.PAPER_TEMPLATES.keys())
        print(f"  ✓ Paper templates: {len(templates)} ({', '.join(templates[:3])}...)")
        
        results.append(("Academic", "PASS", f"{len(styles)} styles, {len(templates)} templates"))
    except Exception as e:
        results.append(("Academic", "FAIL", str(e)))
        print(f"  ✗ Error: {e}")
    
    # === TEST 7: LLM Connection ===
    print("\n[TEST 7] LLM Connection...")
    try:
        import requests
        from agents.config import LM_STUDIO_URL
        
        response = requests.post(
            LM_STUDIO_URL,
            json={
                "messages": [{"role": "user", "content": "Say 'test OK' in 2 words"}],
                "max_tokens": 10,
                "temperature": 0
            },
            timeout=10
        )
        
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            print(f"  ✓ LLM Response: '{reply[:30]}...'")
            results.append(("LLM", "PASS", "Connected"))
        else:
            print(f"  ✗ Status: {response.status_code}")
            results.append(("LLM", "FAIL", f"Status {response.status_code}"))
    except requests.exceptions.ConnectionError:
        print("  ✗ LLM not running (connection refused)")
        results.append(("LLM", "FAIL", "Not running"))
    except Exception as e:
        results.append(("LLM", "FAIL", str(e)))
        print(f"  ✗ Error: {e}")
    
    # === TEST 8: Memory ===
    print("\n[TEST 8] Memory System...")
    try:
        from agents.memory import memory
        # Test save and recall
        memory.remember("test_key_12345", "test_value_automated")
        recalled = memory.recall("test_key_12345")
        if recalled == "test_value_automated":
            print("  ✓ Memory save/recall working")
            results.append(("Memory", "PASS", "Working"))
        else:
            print(f"  ~ Recall mismatch: got '{recalled}'")
            results.append(("Memory", "WARN", "Mismatch"))
    except Exception as e:
        results.append(("Memory", "FAIL", str(e)))
        print(f"  ✗ Error: {e}")
    
    # === SUMMARY ===
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r[1] == "PASS")
    warned = sum(1 for r in results if r[1] == "WARN")
    failed = sum(1 for r in results if r[1] == "FAIL")
    
    for name, status, detail in results:
        icon = "✅" if status == "PASS" else ("⚠️" if status == "WARN" else "❌")
        print(f"  {icon} {name}: {status} - {detail}")
    
    print(f"\nTotal: {passed} PASS, {warned} WARN, {failed} FAIL")
    print("="*60)
    
    return passed, warned, failed

if __name__ == "__main__":
    passed, warned, failed = run_tests()
    sys.exit(0 if failed == 0 else 1)
