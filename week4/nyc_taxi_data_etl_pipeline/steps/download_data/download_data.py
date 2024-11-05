import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def download_data():
    data_dir = os.getenv('DATA_DIR', '/data')
    os.makedirs(data_dir, exist_ok=True)
    months = ['2023-01', '2023-02']
    base_url = 'https://d37ci6vzurychx.cloudfront.net/trip-data'

    for month in months:
        file_name = f'yellow_tripdata_{month}.parquet'
        url = f'{base_url}/{file_name}'
        output_path = os.path.join(data_dir, file_name)

        if not os.path.exists(output_path):
            logger.info(f'Downloading data for {month}...')
            os.system(f'curl -sSL -o {output_path} {url}')
            logger.info(f'Downloaded {file_name}')
        else:
            logger.info(f'File {file_name} already exists. Skipping download.')
