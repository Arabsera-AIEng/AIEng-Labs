import configparser
import pandas as pd

class SchemaValidator:
    def __init__(self, config_path='config.ini'):
        # Load the INI configuration file
        config = configparser.ConfigParser()
        config.read(config_path)

        # Read paths from the configuration
        self.train_schema_path = config['schema_validator']['train_schema_path']
        self.test_schema_path = config['schema_validator']['test_schema_path']
        self.combined_train_path = config['schema_validator']['combined_train']
        self.combined_test_path = config['schema_validator']['combined_test']
        self.final_train_path = config['schema_validator']['final_train']
        self.final_test_path = config['schema_validator']['final_test']

        # Load the schema
        self.schema = self.load_schema(self.train_schema_path)

    def load_schema(self, schema_path):
        """
        Load schema from a CSV file that contains column names and their data types.
        """
        schema_df = pd.read_csv(schema_path)
        schema_df['DataType'] = schema_df['DataType'].apply(self.convert_dtype)
        return schema_df

    @staticmethod
    def convert_dtype(dtype_str):
        """
        Convert a string representation of a data type to a pandas/numpy dtype.
        """
        dtype_mapping = {
            'int': 'int64',
            'float': 'float64',
            'object': 'object',
            'bool': 'bool'
        }
        return dtype_mapping.get(dtype_str.lower(), 'object')

    def validate_schema(self, df, exclude_columns=None):
        if exclude_columns is None:
            exclude_columns = []

        schema_to_validate = self.schema[~self.schema['ColumnName'].isin(exclude_columns)]
        validation_results = {'valid': True, 'missing_columns': [], 'data_type_mismatches': []}

        missing_columns = set(schema_to_validate['ColumnName']) - set(df.columns)
        if missing_columns:
            validation_results['valid'] = False
            validation_results['missing_columns'] = list(missing_columns)

        for _, row in schema_to_validate.iterrows():
            col = row['ColumnName']
            expected_type = row['DataType']
            if col in df.columns:
                if str(df[col].dtype) != expected_type:
                    validation_results['valid'] = False
                    validation_results['data_type_mismatches'].append((col, expected_type, str(df[col].dtype)))

        return validation_results

    def reorder_columns(self, df, exclude_columns=None):
        if exclude_columns is None:
            exclude_columns = []

        columns_to_order = self.schema[~self.schema['ColumnName'].isin(exclude_columns)]['ColumnName'].tolist()
        return df.reindex(columns=[col for col in columns_to_order if col in df.columns])
