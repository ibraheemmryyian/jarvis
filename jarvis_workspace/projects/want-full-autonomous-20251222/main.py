import networkx as nx
import random
import numpy as np
import pandas as pd
from src.simulation import GraphSimulator

def main():
    sim = GraphSimulator(n_nodes=50, p=0.1)
    latency, utilization, centrality = sim.run_simulation(iterations=500)

    print("✅ Simulation completed.")
    print(f"📊 Latency mean: {np.mean(latency):.3f}")
    print(f"📊 Utilization mean: {np.mean(utilization):.3f}")

if __name__ == "__main__":
    main()