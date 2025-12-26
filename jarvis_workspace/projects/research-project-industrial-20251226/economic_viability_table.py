import numpy as np

# Sample data for the table (replace with actual model results)
waste_diversion_percentage = [80, 85, 78, 90, 82]
valorization_revenue = [10000, 12000, 9500, 15000, 13000]
incineration_cost = [5000, 6000, 5500, 7000, 6500]
landfill_cost = [8000, 9000, 8500, 10000, 9500]

# Calculate total cost and net revenue
total_costs = landfill_cost + incineration_cost
net_revenue = valorization_revenue - total_costs

# Create the table
print("| Waste Diversion Percentage | Valorization Revenue ($) | Incineration Cost ($) | Landfill Cost ($) | Total Cost ($) | Net Revenue ($) |")
print("|----------------------------|--------------------------|----------------------|--------------------|---------------|-----------------|")

for i in range(len(waste_diversion_percentage)):
    print(f"| {waste_diversion_percentage[i]}% | {valorization_revenue[i]:,} | {incineration_cost[i]:,} | {landfill_cost[i]:,} | {total_costs[i]:,} | {net_revenue[i]:,} |")