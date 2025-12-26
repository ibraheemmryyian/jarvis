import pandas as pd
import matplotlib.pyplot as plt

# Load the carbon credit calculation results from a CSV file
results = pd.read_csv('calculation_results.csv')

# Group the data by industry and calculate the average carbon credits per tonne
industry_avg_credits = results.groupby('Industry').mean()['Carbon_Credits']

# Create a bar chart of the average carbon credits per tonne by industry
fig, ax = plt.subplots(figsize=(10, 6))
industry_avg_credits.plot(kind='bar', ax=ax)
ax.set_xlabel('Industry')
ax.set_ylabel('Average Carbon Credits (tonnes)')
ax.set_title('Average Carbon Credits by Industry')

# Save the chart to a file
plt.savefig('average_carbon_credits_by_industry.png')

# Group the data by industry and calculate the total carbon credits
industry_total_credits = results.groupby('Industry').sum()['Carbon_Credits']

# Create a pie chart of the total carbon credits by industry
fig, ax = plt.subplots(figsize=(10, 10))
industry_total_credits.plot(kind='pie', autopct='%1.1f%%', startangle=90)
ax.set_title('Total Carbon Credits by Industry')

# Save the chart to a file
plt.savefig('total_carbon_credits_by_industry.png')