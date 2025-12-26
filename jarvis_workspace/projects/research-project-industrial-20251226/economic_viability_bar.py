import matplotlib.pyplot as plt
import numpy as np

# Sample data for the bar chart (replace with actual model results)
waste_diversion_percentage = [80, 85, 78, 90, 82]
valorization_revenue = [10000, 12000, 9500, 15000, 13000]

plt.figure(figsize=(8,6))
plt.bar(waste_diversion_percentage, valorization_revenue)
plt.title('Valorization Revenue vs. Waste Diversion Percentage')
plt.xlabel('Waste Diversion Percentage (%)')
plt.ylabel('Valorization Revenue ($)')

plt.grid(True)
plt.show()