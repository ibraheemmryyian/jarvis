import networkx as nx
import numpy as np
import random
from typing import List, Dict, Tuple

class Agent:
    def __init__(self, id: int, resources: float = 1.0):
        self.id = id
        self.resources = resources
        self.neighbors = []
        self.allocation = None

    def update_allocation(self, neighbors, alpha: float, beta: float):
        # Compute local topology metrics
        degree = len(neighbors)
        clustering = self._compute_clustering(neighbors)
        topology_score = degree * 0.3 + clustering * 0.7  # Simplified metric

        # Compute utility gradient (e.g., resource efficiency)
        utility_gradient = self._compute_utility_gradient(neighbors)

        # Weighted combination
        allocation = alpha * topology_score + beta * utility_gradient

        # Normalize and assign
        self.allocation = np.clip(allocation, 0, 1)
        return self.allocation

    def _compute_clustering(self, neighbors):
        # Simplified clustering coefficient
        if len(neighbors) < 2:
            return 0
        # Assume uniform clustering for now
        return 0.5

    def _compute_utility_gradient(self, neighbors):
        # Example: resource efficiency = 1 / (1 + degree)
        degree = len(neighbors)
        return 1.0 / (1 + degree)

    def random_allocation(self, neighbors):
        # Uniform random allocation
        n = len(neighbors)
        if n == 0:
            return np.array([1.0])
        return np.random.dirichlet([1.0] * n)

class Simulation:
    def __init__(self, topology_type: str, num_agents: int, alpha: float, beta: float):
        self.topology_type = topology_type
        self.num_agents = num_agents
        self.alpha = alpha
        self.beta = beta
        self.graph = self._generate_topology()
        self.agents = self._initialize_agents()
        self.metrics = {
            'mean_efficiency': [],
            'variance': [],
            'convergence_time': []
        }

    def _generate_topology(self):
        if self.topology_type == "ER":
            return nx.erdos_renyi_graph(self.num_agents, p=0.5)
        elif self.topology_type == "BA":
            return nx.barabasi_albert_graph(self.num_agents, m=2)
        elif self.topology_type == "WS":
            return nx.watts_strogatz_graph(self.num_agents, k=4, p=0.1)
        else:
            raise ValueError("Invalid topology type")

    def _initialize_agents(self):
        agents = []
        graph = self.graph
        for i, node in enumerate(graph.nodes):
            agent = Agent(i)
            agent.neighbors = list(graph.neighbors(node))
            agents.append(agent)
        return agents

    def run_step(self):
        # Run one step of simulation
        for agent in self.agents:
            agent.update_allocation(agent.neighbors, self.alpha, self.beta)
        # Collect metrics
        efficiency = np.mean([a.allocation.sum() for a in self.agents])
        variance = np.var([a.allocation.sum() for a in self.agents])
        self.metrics['mean_efficiency'].append(efficiency)
        self.metrics['variance'].append(variance)

    def run(self, iterations: int):
        # Run for specified iterations
        for i in range(iterations):
            self.run_step()
            # Check convergence (optional)
            if i > 10:
                break

    def collect_metrics(self):
        # Return collected metrics
        return self.metrics