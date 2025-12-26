import pandas as pd
import os

file_path = 'jarvis_workspace/mgt1 first initial calls.xlsx'

if not os.path.exists(file_path):
    print("Error: File not found")
else:
    try:
        df = pd.read_excel(file_path)
        print("Dataset Info:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nData types:")
        print(df.dtypes)
        print("\nNull values per column:")
        print(df.isnull().sum())
    except Exception as e:
        print(f"Error reading file: {e}")