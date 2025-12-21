"""
Run Jarvis Autonomous Build and wait for completion.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')

from agents.autonomous import AutonomousExecutor

def main():
    executor = AutonomousExecutor()
    
    objective = """Build the complete Jarvis OS - a business operating system with:
1. Native CRM (contacts, deals, pipeline, activities)
2. Agent Management Dashboard (create/configure AI workers)
3. Manager oversight system (assign tasks, review performance)
4. Internal agent communication (agents chat, escalate to manager)
5. Knowledge base (company docs, SOPs)
6. Automation engine (workflows, triggers)
7. Analytics dashboard (KPIs, reports)

Work autonomously until complete."""

    print("=" * 60)
    print("STARTING JARVIS AUTONOMOUS BUILD")
    print("=" * 60)
    print(f"Objective: {objective[:100]}...")
    print("=" * 60)
    
    result = executor.run(objective)
    
    print("\n" + "=" * 60)
    print("JARVIS BUILD COMPLETE")
    print("=" * 60)
    print(f"Status: {result.get('status')}")
    print(f"Iterations: {result.get('iterations')}")
    print(f"Project Path: {result.get('project_path')}")
    print()
    print("Last 30 log entries:")
    print("-" * 40)
    for entry in result.get('log', [])[-30:]:
        print(entry)
    
    return result

if __name__ == "__main__":
    main()
