"""
Industrial Symbiosis Research Test
A comprehensive autonomous test requiring Jarvis to:
1. Research GRI 306 definitions and save to glossary.md
2. Develop a novel concept in industrial symbiosis
3. Code a simulation
4. Run analysis and get results
5. Write an academic research paper
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.autonomous import AutonomousExecutor

def run_test():
    print("=" * 70)
    print("🔬 INDUSTRIAL SYMBIOSIS RESEARCH TEST")
    print("=" * 70)
    
    objective = """
    RESEARCH PROJECT: Industrial Symbiosis Cost-Benefit Analysis Framework
    
    PART 1 - GRI DEFINITIONS:
    Extract from Global Reporting Initiative (GRI) Standards for Waste Management (GRI 306):
    - Definition of 'Diversion'
    - Definition of 'Valorization' 
    - Definition of 'Incineration'
    - Definition of 'Landfill'
    Save these exact legal definitions to glossary.md
    
    PART 2 - NOVEL RESEARCH:
    Develop a NOVEL concept in industrial symbiosis. Ideas:
    - Regional cost optimization model for waste exchange networks
    - Multi-industry material flow efficiency scoring system
    - Carbon credit calculation framework for symbiotic partnerships
    - Economic viability prediction model for waste-to-resource conversion
    
    PART 3 - SIMULATION:
    Build Python simulation that models your novel concept:
    - simulation.py - Main simulation code
    - data.py - Sample industry data (waste types, volumes, costs)
    - analysis.py - Run simulation and output metrics
    - results/ - Generated charts, CSVs, outputs
    
    PART 4 - ACADEMIC PAPER:
    Write a complete research paper (paper.md) with:
    - Abstract with key findings
    - Introduction to industrial symbiosis
    - Methodology explaining your novel approach
    - Results with actual simulation data
    - Discussion and implications
    - Conclusion
    - References
    
    OUTPUT FILES REQUIRED:
    - glossary.md (GRI 306 definitions)
    - simulation.py (novel concept implementation)
    - data.py (sample data)
    - analysis.py (run and analyze)
    - results/metrics.csv (simulation outputs)
    - paper.md (complete academic paper with real results)
    """
    
    print(f"\n📝 OBJECTIVE:\n{objective[:500]}...\n")
    print("-" * 70)
    
    executor = AutonomousExecutor()
    
    # Allow more iterations for this complex task
    executor.max_iterations = 50
    executor.max_coding_iterations = 30
    
    print("\n🚀 Starting autonomous execution...\n")
    
    start_time = time.time()
    
    try:
        result = executor.run(objective)
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Completed in {elapsed/60:.1f} minutes")
        print(f"📊 Iterations: {executor.iteration}")
        
        # Check generated files
        project_path = os.path.join(
            os.path.dirname(__file__),
            "jarvis_workspace", "projects"
        )
        
        if os.path.exists(project_path):
            print("\n📁 Projects created:")
            for p in sorted(os.listdir(project_path), key=lambda x: os.path.getmtime(os.path.join(project_path, x)), reverse=True)[:3]:
                proj_dir = os.path.join(project_path, p)
                if os.path.isdir(proj_dir):
                    print(f"\n  📂 {p}")
                    for root, dirs, files in os.walk(proj_dir):
                        for f in files:
                            full_path = os.path.join(root, f)
                            rel_path = os.path.relpath(full_path, proj_dir)
                            size = os.path.getsize(full_path)
                            print(f"     • {rel_path} ({size} bytes)")
        
        print("\n✅ TEST COMPLETE")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
