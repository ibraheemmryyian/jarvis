import matplotlib.pyplot as plt
import numpy as np

# Sample data for the pie chart (replace with actual model results)
valorization_revenue = [10000, 12000, 9500, 15000, 13000]
incineration_cost = [5000, 6000, 5500, 7000, 6500]
landfill_cost = [8000, 9000, 8500, 10000, 9500]

# Calculate total costs and net revenue
total_costs = landfill_cost + incineration_cost
net_revenue = valorization_revenue - total_costs

plt.figure(figsize=(8,8))
wedges, texts, autotexts = plt.pie(net_revenue, labels=valorization_revenue, autopct='%1.1f%%', startangle=90)

plt.title('Net Revenue vs. Valorization Revenue')
plt.show()