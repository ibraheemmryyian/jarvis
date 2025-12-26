import matplotlib.pyplot as plt
import numpy as np

# Sample data for the chart (replace with actual model results)
waste_diversion_percentage = [80, 85, 78, 90, 82]
valorization_revenue = [10000, 12000, 9500, 15000, 13000]
incineration_cost = [5000, 6000, 5500, 7000, 6500]
landfill_cost = [8000, 9000, 8500, 10000, 9500]

# Calculate total cost and net revenue
total_costs = landfill_cost + incineration_cost
net_revenue = valorization_revenue - total_costs

# Create the chart
plt.figure(figsize=(10, 6))
plt.plot(waste_diversion_percentage, net_revenue, marker='o', linestyle='-', color='blue')
plt.title('Economic Viability of Industrial Symbiosis')
plt.xlabel('Waste Diversion Percentage (%)')
plt.ylabel('Net Revenue ($)')
plt.grid(True)
plt.fill_between(waste_diversion_percentage, 0, net_revenue, alpha=0.2)

# Display the chart
plt.show()