"""
ATRA-G Simulation Runner
Runs the simulation on all 3 topologies and prints results
"""
from main import Simulation
import json

def run_all_topologies():
    results = {}
    topologies = ["ER", "BA", "WS"]
    
    for topo in topologies:
        print(f"\n🔬 Running {topo} topology simulation...")
        sim = Simulation(
            topology_type=topo,
            num_agents=50,
            alpha=0.7,
            beta=0.3
        )
        sim.run(iterations=100)
        metrics = sim.collect_metrics()
        
        # Summarize
        avg_efficiency = sum(metrics['mean_efficiency']) / len(metrics['mean_efficiency']) if metrics['mean_efficiency'] else 0
        avg_variance = sum(metrics['variance']) / len(metrics['variance']) if metrics['variance'] else 0
        
        results[topo] = {
            "avg_efficiency": round(avg_efficiency, 4),
            "avg_variance": round(avg_variance, 4),
            "iterations": len(metrics['mean_efficiency'])
        }
        
        print(f"  ✅ {topo}: Efficiency={avg_efficiency:.4f}, Variance={avg_variance:.4f}")

    # Save to file
    with open("simulation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n📊 Results saved to simulation_results.json")
    print(json.dumps(results, indent=2))
    
    return results

if __name__ == "__main__":
    run_all_topologies()
