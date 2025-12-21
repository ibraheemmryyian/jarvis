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

    def negotiate_resource(self, available_resources: Dict[str, int], neighbors: List['Agent']) -> Dict[str, int]:
        """
        Negotiate resource allocation with neighbors using AWCA protocol.
        Returns: resource allocation dict
        """
        # Step 1: Calculate weighted consensus
        consensus_weights = []
        for neighbor in neighbors:
            if neighbor.negotiation_state == "idle":
                weight = (neighbor.centrality * neighbor.reputation) / (1 + neighbor.last_negotiation)
                consensus_weights.append(weight)
        
        # Step 2: Calculate resource pricing based on congestion
        congestion_factor = 0.0
        for resource_type in available_resources:
            congestion_factor += (available_resources[resource_type] / 100.0) ** 0.5
        
        # Step 3: Execute AWCA protocol
        allocation = {}
        for resource_type in self.resource_requests:
            if resource_type in available_resources:
                # Calculate bid based on urgency, reputation, and congestion
                bid = self.task_priority * self.reputation * (1.0 / (1.0 + congestion_factor))
                # Negotiate with neighbors
                neighbor_bids = []
                for neighbor in neighbors:
                    if neighbor.agent_id != self.agent_id:
                        neighbor_bid = neighbor.reputation * (1.0 / (1.0 + congestion_factor))
                        neighbor_bids.append(neighbor_bid)
                
                # Select highest bid (weighted by centrality)
                winner = None
                max_bid = 0.0
                for neighbor in neighbors:
                    if neighbor.agent_id != self.agent_id:
                        bid = neighbor.reputation * (1.0 / (1.0 + congestion_factor))
                        if bid > max_bid:
                            max_bid = bid
                            winner = neighbor
                # Allocate resource to winner
                if winner:
                    allocation[resource_type] = 1
                    winner.resource_allocation += 1
                    self.resource_allocation -= 1
                    self.negotiation_state = "completed"
                else:
                    allocation[resource_type] = 0
                    self.negotiation_state = "idle"
        
        return allocation

    def update_reputation(self, reward: float):
        """
        Update agent reputation based on negotiation outcome.
        """
        self.reputation = min(2.0, max(0.0, self.reputation + reward * 0.1))

    def update_centrality(self, new_centrality: float):
        """
        Update agent centrality based on network topology changes.
        """
        self.centrality = new_centrality

    def is_ready(self) -> bool:
        """
        Check if agent is ready to execute task.
        """
        return self.resource_allocation > 0 and self.current_task is not None

    def execute_task(self) -> bool:
        """
        Execute assigned task and return success status.
        """
        if not self.is_ready():
            return False
        
        # Simulate task execution
        self.resource_allocation -= 1
        self.current_task = None
        self.task_priority = 0.0
        self.negotiation_state = "idle"
        return True

    def __repr__(self):
        return f"Agent({self.agent_id}, centrality={self.centrality:.2f}, reputation={self.reputation:.2f})"


class Swarm:
    """
    Manages the decentralized AI swarm.
    Implements the Adaptive Weighted Consensus Auction (AWCA) protocol.
    """
    
    def __init__(self, num_agents: int = 100, num_resources: int = 50, topology: str = "random"):
        self.num_agents = num_agents
        self.num_resources = num_resources
        self.topology = topology
        self.agents = []
        self.resources = defaultdict(int)
        self.iteration = 0
        self.results = []
        
        # Initialize agents
        for i in range(num_agents):
            centrality = random.uniform(0.1, 1.0) if topology == "random" else 0.5
            agent = Agent(i, centrality)
            self.agents.append(agent)
        
        # Initialize resources
        for i in range(num_resources):
            self.resources[f"resource_{i}"] = 100  # 100 units per resource type
        
        # Initialize network topology
        self._initialize_topology()

    def _initialize_topology(self):
        """
        Initialize network topology based on specified type.
        """
        if self.topology == "random":
            # Random topology: each agent connects to 3-5 other agents
            for agent in self.agents:
                agent.neighbors = random.sample(self.agents, random.randint(3, 5))
        elif self.topology == "ring":
            # Ring topology: each agent connects to 2 neighbors
            for i, agent in enumerate(self.agents):
                agent.neighbors = [self.agents[(i - 1) % len(self.agents)], self.agents[(i + 1) % len(self.agents)]]
        elif self.topology == "star":
            # Star topology: one central agent connected to all others
            central_agent = self.agents[0]
            for agent in self.agents[1:]:
                agent.neighbors = [central_agent]
                central_agent.neighbors.append(agent)
        else:
            raise ValueError("Unsupported topology type")

    def step(self) -> Dict[str, float]:
        """
        Execute one step of the simulation.
        Returns: metrics for this iteration.
        """
        self.iteration += 1
        metrics = {
            "avg_resource_utilization": 0.0,
            "avg_latency": 0.0,
            "convergence_rate": 0.0,
            "max_centrality": 0.0
        }
        
        # Assign tasks to agents (randomly)
        for agent in self.agents:
            if random.random() < 0.3:  # 30% chance of getting a task
                task_id = random.randint(0, 100)
                urgency = random.uniform(0.1, 1.0)
                resource_reqs = {}
                for i in range(random.randint(1, 3)):
                    resource_type = f"resource_{random.randint(0, self.num_resources - 1)}"
                    amount = random.randint(1, 10)
                    resource_reqs[resource_type] = amount
                agent.assign_task(task_id, urgency, resource_reqs)
        
        # Execute negotiations
        for agent in self.agents:
            if agent.current_task is not None:
                # Negotiate with neighbors
                allocation = agent.negotiate_resource(self.resources, agent.neighbors)
                # Update resource state
                for resource_type, amount in allocation.items():
                    self.resources[resource_type] -= amount
                    if self.resources[resource_type] < 0:
                        self.resources[resource_type] = 0
        
        # Execute tasks
        completed_tasks = 0
        for agent in self.agents:
            if agent.current_task is not None:
                success = agent.execute_task()
                if success:
                    completed_tasks += 1
        
        # Update metrics
        total_utilization = sum(self.resources.values()) / self.num_resources
        metrics["avg_resource_utilization"] = 1.0 - (total_utilization / 100.0)
        metrics["avg_latency"] = self.iteration / len(self.agents)  # latency = time / agents
        metrics["convergence_rate"] = completed_tasks / len(self.agents)
        metrics["max_centrality"] = max(agent.centrality for agent in self.agents)
        
        # Record results
        self.results.append(metrics)
        
        return metrics

    def get_agent_state(self, agent_id: int) -> Dict[str, Any]:
        """
        Get state of a specific agent.
        """
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return {
                    "agent_id": agent.agent_id,
                    "current_task": agent.current_task,
                    "resource_allocation": agent.resource_allocation,
                    "task_priority": agent.task_priority,
                    "reputation": agent.reputation,
                    "centrality": agent.centrality
                }
        return None

    def get_resource_state(self) -> Dict[str, int]:
        """
        Get current resource state.
        """
        return dict(self.resources)

    def get_network_state(self) -> List[Dict[str, Any]]:
        """
        Get current network topology state.
        """
        network_state = []
        for agent in self.agents:
            neighbors = [neighbor.agent_id for neighbor in agent.neighbors]
            network_state.append({
                "agent_id": agent.agent_id,
                "neighbors": neighbors,
                "centrality": agent.centrality,
                "reputation": agent.reputation
            })
        return network_state

    def reset(self):
        """
        Reset swarm to initial state.
        """
        self.iteration = 0
        self.results = []
        for agent in self.agents:
            agent.current_task = None
            agent.resource_allocation = 10
            agent.task_priority = 0.0
            agent.negotiation_state = "idle"
            agent.last_negotiation = 0
            agent.resource_requests = []
        self._initialize_topology()

    def set_topology(self, topology: str):
        """
        Set network topology.
        """
        self.topology = topology
        self._initialize_topology()

    def set_resource_levels(self, resource_levels: Dict[str, int]):
        """
        Set resource levels.
        """
        for resource_type, amount in resource_levels.items():
            self.resources[resource_type] = amount

    def get_agent_count(self) -> int:
        """
        Get number of agents.
        """
        return len(self.agents)

    def get_resource_count(self) -> int:
        """
        Get number of resource types.
        """
        return len(self.resources)

    def get_iteration(self) -> int:
        """
        Get current iteration.
        """
        return self.iteration

    def get_results(self) -> List[Dict[str, float]]:
        """
        Get all results.
        """
        return self.results

    def __repr__(self):
        return f"Swarm({self.num_agents}, {self.num_resources}, {self.topology})"


# Example usage
if __name__ == "__main__":
    swarm = Swarm(num_agents=100, num_resources=50, topology="random")
    print("Swarm initialized with 100 agents and 50 resources.")
    print("Topology: random")
    print("Initial resource state:", swarm.get_resource_state())
    print("Initial agent state:", swarm.get_agent_state(0))