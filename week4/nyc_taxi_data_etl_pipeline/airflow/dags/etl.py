import pandas as pd
import json
from datetime import datetime

def run_test_etl():
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [24, 27, 22, 32, 29],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    }

    df = pd.DataFrame(data)

    print("DataFrame:")
    print(df)

    df.to_csv('sample_data.csv', index=False)

    print("\nDataFrame saved as 'sample_data.csv'")