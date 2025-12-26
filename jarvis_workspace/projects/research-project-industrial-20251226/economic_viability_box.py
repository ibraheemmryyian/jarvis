import matplotlib.pyplot as plt
import numpy as np

# Sample data for the box plot (replace with actual model results)
waste_diversion_percentage = [80, 85, 78, 90, 82]
valorization_revenue = [10000, 12000, 9500, 15000, 13000]
incineration_cost = [5000, 6000, 5500, 7000, 6500]

plt.figure(figsize=(10,6))
plt.boxplot([waste_diversion_percentage, valorization_revenue, incineration_cost], positions=[1,2,3], widths=0.5)
plt.xticks([1,2,3], ['Waste Diversion', 'Valorization Revenue', 'Incineration Cost'])
plt.title('Economic Viability Metrics Comparison')
plt.grid(True)

plt.show()