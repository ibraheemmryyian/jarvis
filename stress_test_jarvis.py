
import time
import os
import sys

# Ensure we can import agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import orchestrator
from agents.context_manager import context

def print_callback(msg):
    """Real-time feedback printer"""
    print(f"\n{msg}")

def main():
    print("🚀 INITIALIZING JARVIS AUTONOMOUS STRESS TEST")
    print("=============================================")
    
    # 1. Seed User Preferences (The "Guard Rails")
    print("\n[1/3] Seeding User Preferences...")
    preferences = """
- **Preferred Language**: Python for logic/backend, React for frontend.
- **Coding Style**: Clean, modular, type-hinted (where applicable).
- **Research Standards**: rigorous, first-principles thinking. No fluff.
- **Simulation Requirements**: Always run at least 500 iterations for monte carlo simulations.
- **Output Format**: Academic standard for papers. "Nature" journal style.
"""
    context.write("user_preferences", f"# User Preferences\n{preferences}")
    print("✅ User preferences set in .context/user_preferences.md")
    
    # 2. Define the Massive Prompt
    prompt = """
    I want you to act as a full autonomous research lab.
    
    **Goal**: Develop a novel algorithmic concept for "Dynamic Resource Allocation in decentralized AI Swarms".
    
    **Your Mission**:
    1. **Concept**: Refine the "ATRA-G" concept.
    2. **Real Science**: You MUST use `networkx` to generate a REAL graph (e.g., Erdos-Renyi) and calculate REAL Centrality. Do NOT use `random.uniform()`.
    3. **Code Structure**: Create a clean project structure.
       - `src/simulation.py`: The core logic (networkx + agents).
       - `src/main.py`: The entry point.
       - `paper.md`: The report.
    4. **Execute**: Run the simulation code to generate REAL data (latency, utilization).
    5. **Publish**: Write the paper using the REAL data.

    **CRITICAL RULES**:
    - NO MOCK DATA. I will audit your code.
    - NO EMBEDDED CODE in the paper. The paper should reference the files.
    - SAVE YOUR WORK.
    """
    
    print("\n[2/3] Sending Complex Prompt to Orchestrator...")
    print(f"PROMPT PREVIEW: {prompt[:100]}...")
    
    # 3. Execute
    print("\n[3/3] STARTING AUTONOMOUS LOOP")
    print("------------------------------")
    
    result = orchestrator.execute(prompt, callback=print_callback)
    
    print("\n=============================================")
    print("🏁 STRESS TEST INITIATED")
    print("Check jarvis_workspace/projects/ for artifacts.")

if __name__ == "__main__":
    main()
