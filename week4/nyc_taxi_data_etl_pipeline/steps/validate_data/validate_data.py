import os
import logging
import sys
import pandas as pd
import great_expectations as gx

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_data():
    processed_data_dir = os.getenv('PROCESSED_DATA_DIR', '/processed_data')
    months = ['2023-01', '2023-02']

    context = gx.get_context()
    data_source_name = "my_data_source"
    data_asset_name = "my_dataframe_data_asset"
    batch_definition_name = "my_batch_definition"

    # Set up Data Source
    data_source = context.data_sources.add_pandas(name=data_source_name)

    # Add Data Asset
    data_asset = data_source.add_dataframe_asset(name=data_asset_name)

    # Add Batch Definition
    batch_definition = data_asset.add_batch_definition_whole_dataframe(
        batch_definition_name
    )

    for month in months:
        file_path = os.path.join(processed_data_dir, f'processed_data_{month}.csv')

        if not os.path.exists(file_path):
            logger.error(f'Processed data file {file_path} does not exist.')
            continue

        df = pd.read_csv(file_path)
        batch_parameters = {"dataframe": df}

        batch = batch_definition.get_batch(batch_parameters=batch_parameters)

        # Define Expectations
        expectation1 = gx.expectations.ExpectColumnToExist(column="date")
        expectation2 = gx.expectations.ExpectColumnToExist(column="total_amount")
        expectation3 = gx.expectations.ExpectColumnValuesToBeDateutilParseable(column="date")
        expectation4 = gx.expectations.ExpectColumnValuesToBeBetween(
            column="total_amount", min_value=0
        )

        # Validate Expectations
        results = []
        for expectation in [expectation1, expectation2, expectation3, expectation4]:
            validation_result = batch.validate(expectation)
            results.append(validation_result["success"])

        if all(results):
            logger.info(f'Data validation passed for {month}')
        else:
            logger.error(f'Data validation failed for {month}')
            raise ValueError(f'Data validation failed for {month}')

if __name__ == '__main__':
    validate_data()
