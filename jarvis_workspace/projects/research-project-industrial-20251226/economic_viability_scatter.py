import matplotlib.pyplot as plt
import numpy as np

# Sample data for the scatter plot (replace with actual model results)
waste_diversion_percentage = [80, 85, 78, 90, 82]
incineration_cost = [5000, 6000, 5500, 7000, 6500]

plt.figure(figsize=(8,6))
plt.scatter(waste_diversion_percentage, incineration_cost)
plt.title('Incineration Cost vs. Waste Diversion Percentage')
plt.xlabel('Waste Diversion Percentage (%)')
plt.ylabel('Incineration Cost ($)')

plt.grid(True)
plt.show()