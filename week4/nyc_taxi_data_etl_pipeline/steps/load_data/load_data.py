import os
import logging
import sys
import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    processed_data_dir = os.getenv('PROCESSED_DATA_DIR', '/processed_data')
    db_user = os.getenv('DB_USER', 'airflow')
    db_password = os.getenv('DB_PASSWORD', 'airflow')
    db_host = os.getenv('DB_HOST', 'postgres')  # Updated default to 'postgres'
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'airflow')   # Updated default to 'airflow'

    engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    months = ['2023-01', '2023-02']

    for month in months:
        file_path = os.path.join(processed_data_dir, f'processed_data_{month}.csv')

        if not os.path.exists(file_path):
            logger.error(f'Processed data file {file_path} does not exist.')
            continue

        try:
            logger.info(f'Loading data for {month} into PostgreSQL...')
            df = pd.read_csv(file_path)
            df.to_sql('daily_totals', engine, if_exists='append', index=False)
            logger.info(f'Data for {month} loaded into PostgreSQL.')
        except Exception as e:
            logger.exception(f'Error loading data for {month}: {e}')

if __name__ == '__main__':
    load_data()
