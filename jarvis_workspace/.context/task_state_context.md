# TASK_STATE Context


<!-- ENTRY: 2025-12-22 01:29:59 -->
# Task: 20251222_012959
        
**Objective:** 
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
    

**Steps:**
- [ ] PHASE 1: ARCHITECTURE**
- [ ] [ARCHITECTURE] Create complete system design document with data models, API specs, file structure**
- [ ] Data Models**:
- [ ] `Agent`: id, resource_capacity, latency, current_task, centrality_score, state (idle/active/failed)
- [ ] `Edge`: source_agent, target_agent, weight (latency or bandwidth)
- [ ] `Graph`: nodes (agents), edges (connections), centrality_metrics (betweenness, degree, closeness)
- [ ] API Specs** (Internal only — simulation-driven):
- [ ] `simulate_graph()` → generates Erdos-Renyi graph with `n=100`, `p=0.05`
- [ ] `compute_centrality()` → calculates betweenness, degree, closeness for all nodes
- [ ] `allocate_resources()` → assigns tasks to agents based on centrality + latency
- [ ] `collect_metrics()` → outputs latency, utilization, throughput, failure_rate
- [ ] File Structure**:
- [ ] [ARCHITECTURE] Define component boundaries and integration points**
- [ ] Component Boundaries**:
- [ ] `simulation.py`: Handles graph generation, centrality calculation, task allocation logic.
- [ ] `agents.py`: Defines Agent class with state transitions, resource consumption, and latency modeling.
- [ ] `main.py`: Orchestrates simulation runs, logs results, triggers data export.
- [ ] Integration Points**:
- [ ] `simulation.py` → `agents.py`: Passes graph structure to agents for state updates.
- [ ] `agents.py` → `simulation.py`: Reports latency, utilization, and state changes.
- [ ] `main.py` → `simulation.py`: Calls `simulate_graph()` and `collect_metrics()`.
- [ ] `main.py` → `paper.md`: Writes final report with metrics.
- [ ] [ARCHITECTURE] Create project skeleton with proper folder structure**
- [ ] Create directories**:
- [ ] Install dependencies**:

<!-- /ENTRY -->
