# TASK_STATE Context


<!-- ENTRY: 2025-12-22 17:13:50 -->
# Task: 20251222_171350
        
**Objective:** 
    I want you to act as a full autonomous research lab.
    
    **Goal**: Develop a novel algorithmic concept for "Dynamic Resource Allocation in decentralized AI Swarms".
    
    **Your Mission**:
    1. **Concept**: Refine the "ATRA-G" concept.
    2. **Real Science (Advanced)**:
       - **Robustness**: Test on THREE topologies: Erdős–Rényi, Barabasi-Albert (Scale-Free), and Watts-Strogatz (Small-World).
       - **Ablation Study**: You MUST run a Control Group (Random Allocation) vs Experimental Group (ATRA-G) to prove the "Topology" term actually matters.
       - **Sensitivity**: Vary the alpha/beta parameters to find the optimal configuration.
    3. **Code Structure**:
       - `src/simulation.py`: The core logic (networkx + agents).
       - `src/main.py`: The entry point that runs all 3 topologies.
       - `paper.md`: The report.
    4. **Execute**: Run the simulation code to generate REAL data.
    5. **Publish**: Write the paper using the REAL data.

    **CRITICAL RULES**:
    - NO MOCK DATA. The "Devils Advocate" is watching. If you fake it, you fail.
    - OUTPUT THE CODE BLOCKS. You must output the full python code for `simulation.py` so it can be saved.
    - SAVE YOUR WORK.
    

**Steps:**
- [ ] PHASE 1: ARCHITECTURE (Steps 1–3)**
- [ ] [ARCHITECTURE] Create complete system design document with data models, API specs, file structure**
- [ ] System Design Document (Draft)**
- [ ] Core Concept: ATRA-G (Adaptive Topology-Responsive Allocation with Gradient Optimization)**
- [ ] Goal**: Dynamically allocate computational resources among agents in a decentralized swarm based on local topology awareness and gradient-based optimization.
- [ ] Key Components**:
- [ ] `Agent`: Represents an AI node with state (resource demand, latency, topology awareness).
- [ ] `Topology`: Graph structure (Erdős–Rényi, Barabasi-Albert, Watts-Strogatz) defining connectivity.
- [ ] `ResourcePool`: Centralized (simulated) pool of compute units; distributed in reality.
- [ ] `GradientOptimizer`: Computes local resource gradients using topology-aware heuristics.
- [ ] `Scheduler`: Decides allocation per agent per time step.
- [ ] Data Models**
- [ ] Simulation State Model
- [ ] ATRA-G Parameters
- [ ] File Structure**
- [ ] [ARCHITECTURE] Define component boundaries and integration points**
- [ ] Component Boundaries**
- [ ] `simulation.py`**
- [ ] Role**: Core simulation engine.
- [ ] Interfaces**:
- [ ] `initialize_topology(topology_config)` → returns NetworkX graph
- [ ] `initialize_agents(n_agents, topology)` → returns list of Agent objects
- [ ] `run_step()` → runs one time step, updates metrics
- [ ] `get_metrics()` → returns performance metrics for analysis
- [ ] `set_params(alpha, beta)` → updates ATRA-G parameters

<!-- /ENTRY -->
