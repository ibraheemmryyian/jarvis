import pandas as pd
import os

# Read the Excel file
file_path = 'jarvis_workspace/mgt1 first initial calls.xlsx'
df = pd.read_excel(file_path)

# Display basic info about the dataframe
print('Columns:', df.columns.tolist())
print('Shape:', df.shape)
print(df.head())