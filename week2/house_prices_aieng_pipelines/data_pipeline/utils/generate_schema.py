import pandas as pd


def generate_schema_csv(input_file, output_file='test_schema.csv'):
    """
    Generate a schema CSV file based on the input CSV file.
    The schema CSV will contain columns: ColumnName and DataType.

    Parameters:
    - input_file: str, path to the input CSV file.
    - output_file: str, path to save the schema CSV file (default: 'schema.csv').
    """
    # Read the input CSV to get the column names and data types
    df = pd.read_csv(input_file)

    # Create a DataFrame for schema
    schema_df = pd.DataFrame({
        'ColumnName': df.columns,
        'DataType': df.dtypes.astype(str)  # Convert the data types to string for saving in CSV
    })

    # Save schema to CSV
    schema_df.to_csv(output_file, index=False)
    print(f"Schema file generated and saved to {output_file}")


# Generate schema from train.csv (or any other CSV file)
generate_schema_csv('../artifacts/test.csv')
