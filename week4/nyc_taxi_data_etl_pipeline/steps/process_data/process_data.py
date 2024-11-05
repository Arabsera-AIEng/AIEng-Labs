import os
import logging
import sys
import pandas as pd

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def process_data():
    data_dir = os.getenv('DATA_DIR', '/data')
    processed_data_dir = os.getenv('PROCESSED_DATA_DIR', '/processed_data')
    os.makedirs(processed_data_dir, exist_ok=True)

    months = ['2023-01', '2023-02']

    for month in months:
        input_file = os.path.join(data_dir, f'yellow_tripdata_{month}.parquet')
        output_file = os.path.join(processed_data_dir, f'processed_data_{month}.csv')

        if not os.path.exists(input_file):
            logger.error(f'Input file {input_file} does not exist.')
            continue

        try:
            logger.info(f'Processing data for {month}...')
            df = pd.read_parquet(input_file)

            # Transformation logic
            df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
            df['date'] = df['tpep_pickup_datetime'].dt.date
            daily_totals = df.groupby('date').agg({'total_amount': 'sum'}).reset_index()

            daily_totals.to_csv(output_file, index=False)
            logger.info(f'Processed data saved to {output_file}')
        except Exception as e:
            logger.exception(f'Error processing data for {month}: {e}')

if __name__ == '__main__':
    process_data()
