"""
Jarvis Live Status Audit
Comprehensive check of all system components
"""
import os
import sys
sys.path.insert(0, '.')

print('=' * 60)
print('JARVIS LIVE STATUS AUDIT')
print('=' * 60)
print()

results = {"pass": 0, "fail": 0, "warn": 0}

# 1. Core Imports
print('[1] CORE IMPORTS')
try:
    from agents.registry import registry
    from agents.orchestrator import Orchestrator
    from agents.autonomous import AutonomousExecutor
    from agents.router import router
    from agents.memory import memory
    print('    [OK] All core modules import successfully')
    results["pass"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 2. Registry Status
print()
print('[2] AGENT REGISTRY')
try:
    status = registry.get_status()
    print(f'    Registered Agents: {status["registered_agents"]}')
    print(f'    Categories: {len(status["categories"])}')
    for cat, agents in status['categories'].items():
        print(f'      - {cat}: {len(agents)} agents')
    results["pass"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 3. Orchestrator
print()
print('[3] ORCHESTRATOR')
try:
    orch = Orchestrator()
    print(f'    Direct Agents: {len(orch.agents)}')
    print(f'    Team Mode: {orch.team_mode}')
    results["pass"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 4. Router
print()
print('[4] ROUTER CLASSIFICATION')
try:
    tests = [
        ('Build a website', 'development'),
        ('Research quantum computing', 'research'),
        ('Analyze competitor', 'business'),
    ]
    all_ok = True
    for query, expected in tests:
        result = router.classify(query)
        cat = result.get('category')
        ok = cat == expected
        status = 'OK' if ok else 'WARN'
        if not ok:
            all_ok = False
        print(f'    [{status}] "{query[:30]}" -> {cat}')
    if all_ok:
        results["pass"] += 1
    else:
        results["warn"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 5. Memory
print()
print('[5] MEMORY SYSTEM')
try:
    memory.remember('audit_test', 'Live audit successful')
    print('    [OK] Memory working')
    results["pass"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 6. Project Builder
print()
print('[6] PROJECT BUILDER')
try:
    from agents.project_builder import project_builder
    templates = list(project_builder.TEMPLATES.keys())
    print(f'    [OK] Templates: {templates}')
    results["pass"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 7. Autonomy Utils
print()
print('[7] AUTONOMY UTILITIES')
try:
    from agents.utils.checkpoint import checkpoint_manager
    from agents.utils.escalation import escalation_manager
    from agents.utils.error_journal import error_journal
    from agents.utils.hierarchical_planner import hierarchical_planner
    print('    [OK] checkpoint_manager')
    print('    [OK] escalation_manager')
    print('    [OK] error_journal')
    print('    [OK] hierarchical_planner')
    results["pass"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 8. LLM Connection
print()
print('[8] LLM CONNECTION')
try:
    import requests
    resp = requests.get('http://localhost:1234/v1/models', timeout=5)
    if resp.status_code == 200:
        models = resp.json().get('data', [])
        if models:
            print(f'    [OK] LM Studio running, model: {models[0].get("id", "unknown")}')
            results["pass"] += 1
        else:
            print('    [WARN] LM Studio running but no model loaded')
            results["warn"] += 1
    else:
        print(f'    [WARN] LM Studio returned {resp.status_code}')
        results["warn"] += 1
except requests.exceptions.ConnectionError:
    print('    [FAIL] LM Studio not running at localhost:1234')
    results["fail"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 9. Workspace
print()
print('[9] WORKSPACE')
try:
    workspace = 'jarvis_workspace'
    projects = os.path.join(workspace, 'projects')
    if os.path.exists(projects):
        project_list = [d for d in os.listdir(projects) if os.path.isdir(os.path.join(projects, d))]
        print(f'    [OK] {len(project_list)} projects in workspace')
        for p in project_list[-5:]:
            print(f'      - {p}')
        results["pass"] += 1
    else:
        print('    [WARN] No projects directory')
        results["warn"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# 10. Context Retriever
print()
print('[10] CONTEXT RETRIEVER')
try:
    from agents.context_retriever import get_context
    ctx = get_context("Build a React app", "frontend_dev")
    print(f'    [OK] Retrieved {len(ctx)} chars context')
    results["pass"] += 1
except Exception as e:
    print(f'    [FAIL] {e}')
    results["fail"] += 1

# Summary
print()
print('=' * 60)
total = results["pass"] + results["fail"] + results["warn"]
print(f'AUDIT RESULTS: {results["pass"]}/{total} PASSED')
print(f'  Passed: {results["pass"]}')
print(f'  Warnings: {results["warn"]}')
print(f'  Failed: {results["fail"]}')
print('=' * 60)

if results["fail"] == 0:
    print('[SUCCESS] SYSTEM OPERATIONAL')
else:
    print('[ISSUES] Some components need attention')
