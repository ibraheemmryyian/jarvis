"""
Jarvis Overnight AI Research Test v2
=====================================
FIXED: Verification gate, context clearing, anti-recycling prompt

Run this script and let Jarvis work overnight.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import autonomous_executor, recycler

OBJECTIVE = """
# AI RESEARCH TASK: Create a GENUINELY NOVEL Algorithm

⚠️ CRITICAL: You must invent something NEW. Do NOT reuse ATRA-G or any algorithm from previous sessions.

## 1. INVENT a GENUINELY NOVEL Algorithm

Research existing approaches in ONE of these areas and propose a COMPLETELY NEW improvement:
- Efficient attention mechanisms - propose a NEW variant (NOT sparse attention, NOT ATRA-G)
- Adaptive learning rates - propose a NEW scheduling algorithm
- Neural architecture search - propose a NEW search strategy
- Gradient optimization - propose a NEW optimizer

REQUIREMENTS FOR NOVELTY:
- Must have a NEW NAME (not ATRA-G, not anything used before)
- Must have a DIFFERENT core mechanism than previous work
- If you find yourself writing "ATRA-G" or "topology-aware", STOP and think of something else

## 2. IMPLEMENT It Fully

Write COMPLETE Python code:
- algorithm.py - Your COMPLETE algorithm implementation (not stubs)
- baseline.py - The baseline you're comparing against
- benchmark.py - Test harness that ACTUALLY RUNS both and outputs metrics

The code must:
- Import only standard libraries + torch/numpy
- Be syntactically correct (we will run python -c "import ast; ast.parse(...)")
- Actually execute without errors

## 3. RUN Benchmarks and Capture Results

You MUST actually execute the benchmark:
1. Create results/ directory
2. Run: python benchmark.py
3. Capture output to results/benchmark_results.csv

The CSV must contain REAL measured numbers, NOT placeholders.
If you write "[X%]" or "[placeholder]" you have FAILED.

## 4. WRITE Complete Academic Paper

Create paper.md with ALL of these sections FULLY WRITTEN:

1. **Title** - Descriptive name for your algorithm (NOT ATRA-G)
2. **Abstract** (150-200 words) - Complete summary
3. **Introduction** - Problem statement, motivation, contributions
4. **Related Work** - At least 3 referenced approaches
5. **Method** - Your algorithm with equations/pseudocode
6. **Experiments** - Exact setup, what you measured
7. **Results** - ACTUAL NUMBERS from benchmark_results.csv
8. **Discussion** - Limitations, why it works/doesn't
9. **Conclusion** - Summary of contributions
10. **References** - At least 5 citations

NO PLACEHOLDERS. Every section must be complete.

## VERIFICATION CHECKLIST (You will fail if missing):
□ paper.md exists with all sections filled
□ algorithm.py exists and has valid Python syntax
□ benchmark.py exists and has valid Python syntax  
□ results/benchmark_results.csv exists with real data
□ NO "[TODO]", "[PLACEHOLDER]", "[Include...]" markers anywhere
□ Algorithm name is NOT "ATRA-G"

## OUTPUT LOCATION:
Save everything to: jarvis_workspace/projects/ai-research-[date]/
"""

def main():
    print("=" * 60)
    print("JARVIS AI RESEARCH TEST v2")
    print("WITH: Verification gate, context clearing, anti-recycling")
    print("=" * 60)
    print(f"\nObjective: Novel AI Algorithm Research")
    print(f"Expected outputs:")
    print(f"  - algorithm.py (novel implementation)")
    print(f"  - baseline.py (comparison)")
    print(f"  - benchmark.py (test harness)")
    print(f"  - results/benchmark_results.csv (real data)")
    print(f"  - paper.md (complete academic paper)")
    print("=" * 60)
    
    # Set the task in recycler
    recycler.set_task(OBJECTIVE, [])
    
    # Run autonomous executor
    result = autonomous_executor.run(OBJECTIVE)
    
    print("\n" + "=" * 60)
    print("OVERNIGHT TEST COMPLETE")
    print("=" * 60)
    
    if result.get("status") == "complete":
        print(f"✅ Completed {result.get('iterations', 0)} iterations")
        print(f"📁 Check: {result.get('project_path', 'jarvis_workspace/projects/')}")
    else:
        print(f"❌ Status: {result.get('status', 'unknown')}")
        if result.get("error"):
            print(f"Error: {result['error']}")
    
    # Print last 30 log entries
    if result.get("log"):
        print("\n--- Last 30 Log Entries ---")
        for entry in result["log"][-30:]:
            print(entry)

if __name__ == "__main__":
    main()
