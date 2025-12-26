import numpy as np
from networkx import adjacency_matrix, degree

class Swarm:
    def __init__(self, num_agents, num_resources, topology):
        self.num_agents = num_agents
        self.num_resources = num_resources
        self.topology = topology
        self.agents = self.initialize_agents()
        self.resources = self.initialize_resources()

    def initialize_agents(self):
        # Initialize agents with random positions and affinities
        return [Agent() for _ in range(self.num_agents)]

    def initialize_resources(self):
        # Initialize resources with random values
        return [Resource() for _ in range(self.num_resources)]

    def step(self):
        """
        Execute one time-step of the swarm simulation.
        Agents allocate resources based on topology-aware affinity matrices.
        """
        for agent in self.agents:
            # Agent perceives local neighborhood and computes affinity matrix
            agent.perceive(self)
            agent.compute_affinity_matrix()

            # Agent allocates resources to tasks based on resource allocation policy
            agent.allocate_resources()

    def get_metrics(self):
        """
        Collect performance metrics after each simulation step.
        """
        utilization = self.calculate_utilization()
        latency = self.calculate_latency()
        convergence_rate = self.calculate_convergence_rate()

        return {
            "iteration": len(results),
            "resource_utilization": np.mean(utilization),
            "task_completion_latency": np.mean(latency),
            "convergence_rate": np.mean(convergence_rate)
        }

    def calculate_utilization(self):
        """
        Calculate the average resource utilization across all agents.
        """
        utilizations = []
        for agent in self.agents:
            utilizations.append(agent.resource_utilization)
        return utilizations

    def calculate_latency(self):
        """
        Calculate the average task completion latency across all agents.
        """
        latencies = []
        for agent in self.agents:
            latencies.append(agent.task_completion_latency)
        return latencies

    def calculate_convergence_rate(self):
        """
        Calculate the convergence rate of each agent's resource allocation policy.
        """
        rates = []
        for agent in self.agents:
            rates.append(agent.convergence_rate)
        return rates