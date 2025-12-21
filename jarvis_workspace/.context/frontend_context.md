# FRONTEND Context

<!-- ENTRY: 2025-12-22 00:38:47 -->
### File Structure**:
```markdown
# File Structure for "Dynamic Resource Allocation in Decentralized AI Swarms" Simulation

## Directory Structure
```
project/
├── main.py
├── swarm.py
├── analysis.py
├── Paper.md
├── README.md
└── requirements.txt
```

## File Descriptions

### `main.py`
- Entry point for the simulation.
- Initializes the swarm, runs the simulation for 500 iterations, and collects results.
- Calls `swarm.py` to manage agent interactions and `analysis.py` to process results.

### `swarm.py`
- Core logic for agent behavior, resource allocation, and topology-aware decision-making.
- Implements the Affinity Matrix and Resource Allocation Policy.
- Manages task assignment, learning rates, and centrality calculations.

### `analysis.py`
- Processes simulation results.
- Computes metrics: resource utilization, task completion latency, and convergence rates.
- Generates visualizations (if terminal agent were active).

### `Paper.md`
- Final academic paper in Nature-style format.
- Includes Title, Abstract, Methodology, Results, Conclusion.

### `README.md`
- Project overview, usage instructions, and dependencies.

### `requirements.txt`
- Lists Python dependencies for the simulation.

---

## NEXT STEP
I will now generate the complete code for `main.py`, `swarm.py`, and `analysis.py` as per the simulation specification.

[COMMAND]: mkdir -p project && touch project/main.py project/swarm.py project/analysis.py project/Paper.md project/README.md project/requirements.txt

[COMMAND]: echo "numpy, networkx, matplotlib, pandas" > project/requirements.txt

[COMMAND]: echo "# Dynamic Resource Allocation in Decentralized AI Swarms\n\nThis project simulates a decentralized swarm of AI agents allocating resources based on topology-aware affinity matrices. The simulation runs 500 iterations and outputs performance metrics." > project/README.md

---

## CODE GENERATION

### `project/main.py`
```python
import os
import sys
import time
import random
import numpy as np
from swarm import Swarm

<!-- /ENTRY -->
<!-- ENTRY: 2025-12-22 00:41:10 -->
### Component Boundaries**:
```python
import os
import sys
import time
import random
import numpy as np
from swarm import Swarm
from analysis import analyze_simulation

def main():
    """
    Main execution function for the decentralized AI swarm simulation.
    Runs 500 iterations, collects metrics, and outputs results.
    """
    print("Initializing decentralized AI swarm simulation...")
    print("Running 500 iterations with topology-aware resource allocation...")

    # Initialize swarm with 100 agents, 50 resources, and random topology
    swarm = Swarm(num_agents=100, num_resources=50, topology="random")

    # Run simulation for 500 iterations
    results = []
    for iteration in range(500):
        print(f"Iteration {iteration + 1}/500...")
        # Execute one step of the swarm simulation
        iteration_result = swarm.step()
        results.append(iteration_result)

        # Optional: Sleep for 0.01s to simulate real-time behavior
        time.sleep(0.01)

    # Analyze results
    metrics = analyze_simulation(results)

    # Output summary
    print("\n=== SIMULATION COMPLETE ===")
    print(f"Average Resource Utilization: {metrics['avg_resource_utilization']:.4f}")
    print(f"Average Task Completion Latency: {metrics['avg_latency']:.4f}")
    print(f"Convergence Rate: {metrics['convergence_rate']:.4f}")
    print(f"Max Centrality Score: {metrics['max_centrality']:.4f}")

    # Save results to file
    with open("results.txt", "w") as f:
        f.write(f"Simulation completed at {time.ctime()}\n")
        f.write(f"Average Resource Utilization: {metrics['avg_resource_utilization']:.4f}\n")
        f.write(f"Average Task Completion Latency: {metrics['avg_latency']:.4f}\n")
        f.write(f"Convergence Rate: {metrics['convergence_rate']:.4f}\n")
        f.write(f"Max Centrality Score: {metrics['max_centrality']:.4f}\n")

    print("Results saved to 'results.txt'")

if __name__ == "__main__":
    main()
```

---

### `project/swarm.py`
```python
import random
import numpy as n
<!-- /ENTRY -->
<!-- ENTRY: 2025-12-22 00:48:19 -->
### `swarm.py`: Manages agent lifecycle, task assignment, negotiation protocol, and resource allocation.
```python
# project/swarm.py
"""
Dynamic Resource Allocation in Decentralized AI Swarms

This module implements a decentralized swarm architecture where agents negotiate and allocate resources using a novel mathematical protocol: the "Adaptive Weighted Consensus Auction (AWCA)".

The AWCA protocol combines:
- Weighted consensus voting based on agent centrality and task urgency
- Dynamic resource pricing based on congestion and agent reputation
- Local negotiation with global convergence guarantees

Agents maintain state, negotiate with neighbors, and update resource allocations in a fully decentralized manner.
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Any
from collections import defaultdict
import math

class Agent:
    """
    Represents an agent in the swarm.
    Each agent has:
    - ID
    - Current task (if any)
    - Resource requirements
    - Reputation score
    - Centrality score (based on network topology)
    - Negotiation state
    """
    
    def __init__(self, agent_id: int, centrality: float, initial_resources: int = 10):
        self.agent_id = agent_id
        self.centrality = centrality
        self.reputation = 1.0  # [0, 2] scale: 0 = untrustworthy, 2 = highly trustworthy
        self.current_task = None
        self.resource_allocation = initial_resources
        self.task_priority = 0.0  # [0, 1] scale: 0 = low priority, 1 = high priority
        self.last_negotiation = 0  # timestamp for negotiation cooldown
        self.negotiation_state = "idle"  # "idle", "negotiating", "completed"
        self.resource_requests = []  # list of (resource_type, amount, urgency)

    def assign_task(self, task_id: int, urgency: float, resource_requirements: Dict[str, int]):
        """
        Assign a new task to the agent.
        """
        self.current_task = task_id
        self.task_priority = urgency
        self.resource_requests = resource_requirements
        return True

    def negotiate_resource(self, availab
<!-- /ENTRY -->