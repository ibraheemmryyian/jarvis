import matplotlib.pyplot as plt
import numpy as np

# Sample data for regional cost optimization model results
regions = ['North', 'South', 'East', 'West']
cost_benefits_2020 = [10000, 15000, 12000, 20000]
cost_benefits_2021 = [15000, 18000, 16000, 22000]

# Generate stacked bar charts for cost benefits in each region
fig, ax = plt.subplots(figsize=(8, 6))

# Stacked bar chart for 2020 cost benefits
bars = ax.bar(regions, cost_benefits_2021)
ax.set_title('Regional Cost Benefits in 2021')
ax.set_xlabel('Region')
ax.set_ylabel('Cost Benefit ($)')
ax.grid(True)

# Annotate each bar with the value
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:,.0f}', xy=(bar.get_x() + bar.get_width()/2, height),
               xytext=(0, 10), textcoords='offset points', ha='center', va='bottom')

plt.savefig('regional_cost_benefits.png')
plt.show()