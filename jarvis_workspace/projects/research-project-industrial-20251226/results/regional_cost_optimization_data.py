import numpy as np
import pandas as pd

# Generate sample data for regional cost optimization model
regions = ['North', 'South', 'East', 'West']
costs = np.random.randint(10000, 50000, size=(4,))
optimization_ratios = np.random.uniform(0.1, 0.5, size=(4,))

data = {
    'Region': regions,
    'Cost (USD)': costs.tolist(),
    'Optimization Ratio': optimization_ratios.tolist()
}

df = pd.DataFrame(data)
df.to_csv('results/regional_cost_optimization_data.csv', index=False)