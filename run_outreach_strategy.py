"""
Run Jarvis Autonomous Mode - Outreach Strategy for Industrial Symbiosis Marketplace
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')

from agents.autonomous import AutonomousExecutor

def main():
    executor = AutonomousExecutor()
    
    objective = """Analyze my business (Industrial Symbiosis Marketplace - a B2B platform connecting waste generators with waste processors for circular economy) and the POC contacts Excel file at 'jarvis_workspace/mgt1 first initial calls.xlsx'.

TASK:
1. Read and analyze the Excel file containing POC contacts (F&B companies in UAE and KSA)
2. Identify the highest-priority prospects based on:
   - Known sustainability initiatives (Agthia has Veolia partnership)
   - Decision-maker contacts available (CEOs, Directors)
   - Company size and waste potential
3. Create a personalized cold outreach strategy for Sunday and Monday including:
   - Prioritized list of who to contact first
   - Personalized email templates for C-suite vs Operations contacts
   - Call scripts for follow-up
   - Timing recommendations (best times to reach Gulf region contacts)
4. Output all deliverables to jarvis_workspace/outreach_strategy/

Work autonomously until complete. Focus on quality over quantity - I need actionable outreach I can execute this weekend."""

    print("=" * 60)
    print("JARVIS AUTONOMOUS MODE - OUTREACH STRATEGY")
    print("=" * 60)
    print(f"Objective: {objective[:200]}...")
    print("=" * 60)
    
    result = executor.run(objective)
    
    print("\n" + "=" * 60)
    print("JARVIS COMPLETE")
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
