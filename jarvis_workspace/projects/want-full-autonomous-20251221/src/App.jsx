import React, { useState, useEffect } from 'react';
import AgentVisualization from './AgentVisualization';
import SimulationControls from './SimulationControls';

function App() {
  const [iterations, setIterations] = useState(500);
  const [topology, setTopology] = useState('random-ring');
  const [results, setResults] = useState({});

  useEffect(() => {
    const simulator = new MonteCarloSimulator(10, iterations);
    const data = simulator.run();
    setResults(data);
  }, [iterations, topology]);

  return (
    <div className="App">
      <h1>DRA-RL Simulation Dashboard</h1>
      <SimulationControls
        iterations={iterations}
        setIterations={setIterations}
        topology={topology}
        setTopology={setTopology}
      />
      <AgentVisualization results={results} />
      <div className="metrics">
        <p>Utilization Efficiency: {results.avg_utilization_efficiency.toFixed(2)}%</p>
        <p>Convergence Speed: {results.avg_convergence_speed.toFixed(2)}%</p>
      </div>
    </div>
  );
}

export default App;