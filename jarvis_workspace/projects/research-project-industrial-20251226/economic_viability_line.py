import matplotlib.pyplot as plt
import numpy as np

# Sample data for the line chart (replace with actual model results)
waste_diversion_percentage = [80, 85, 78, 90, 82]
net_revenue = [5000, 6000, 5500, 7000, 6500]

plt.figure(figsize=(8,6))
plt.plot(waste_diversion_percentage, net_revenue)
plt.title('Net Revenue vs. Waste Diversion Percentage')
plt.xlabel('Waste Diversion Percentage (%)')
plt.ylabel('Net Revenue ($)')

plt.grid(True)
plt.show()