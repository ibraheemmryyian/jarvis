"""
SymbioFlow Test - Cofounder Mode
Tests if Jarvis can handle a vague prompt without adding unwanted features.
"""
import sys
import os
import time

# Add the jarvis directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.autonomous import AutonomousExecutor

def run_test():
    print("=" * 60)
    print("🧪 COFOUNDER MODE TEST - SymbioFlow")
    print("=" * 60)
    
    # A vague, founder-style prompt
    objective = """
    hey need a simple dashboard widget for symbioflow that shows 
    how many companies are connected this week, keep it minimal 
    just a react component nothing crazy
    """
    
    print(f"\n📝 VAGUE PROMPT:\n{objective.strip()}\n")
    print("-" * 60)
    
    executor = AutonomousExecutor()
    
    # Limit iterations for test
    executor.max_iterations = 10
    executor.max_coding_iterations = 5
    
    print("\n🚀 Starting autonomous execution...\n")
    
    start_time = time.time()
    
    try:
        result = executor.run(objective)
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Completed in {elapsed:.1f}s")
        print(f"📊 Iterations: {executor.iteration}")
        
        # Check what was generated
        project_path = os.path.join(
            os.path.dirname(__file__),
            "jarvis_workspace", "projects"
        )
        
        if os.path.exists(project_path):
            print("\n📁 Projects created:")
            for p in os.listdir(project_path):
                proj_dir = os.path.join(project_path, p)
                if os.path.isdir(proj_dir) and "symbio" in p.lower():
                    print(f"  → {p}")
                    # List files
                    for root, dirs, files in os.walk(proj_dir):
                        for f in files:
                            rel_path = os.path.relpath(
                                os.path.join(root, f), proj_dir
                            )
                            size = os.path.getsize(os.path.join(root, f))
                            print(f"     {rel_path} ({size} bytes)")
        
        print("\n✅ TEST COMPLETE")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
