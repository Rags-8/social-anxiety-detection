import pandas as pd

try:
    df = pd.read_csv('Combined Data.csv')
    print("Unique values in 'status' column:", df['status'].unique())
    print("Value counts:\n", df['status'].value_counts())
except Exception as e:
    print(e)
