from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
from docker.types import Mount
import os

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Paths on the host machine
# HOST_DATA_DIR = os.path.abspath('data')
# HOST_PROCESSED_DATA_DIR = os.path.abspath('processed_data')

# Paths on the host machine
# HOST_DATA_DIR = '/Users/amenshawy/Documents/teaching/arabsera/AIEng-Labs/week4/nyc_taxi_data_etl_pipeline/airflow/data'
# HOST_PROCESSED_DATA_DIR = '/Users/amenshawy/Documents/teaching/arabsera/AIEng-Labs/week4/nyc_taxi_data_etl_pipeline/airflow/processed_data'

# Paths on the host machine from environment variables
HOST_DATA_DIR = os.getenv('HOST_DATA_DIR', '/opt/airflow/data')
HOST_PROCESSED_DATA_DIR = os.getenv('HOST_PROCESSED_DATA_DIR', '/opt/airflow/processed_data')

# Paths inside the DockerOperator containers
CONTAINER_DATA_DIR = '/data'
CONTAINER_PROCESSED_DATA_DIR = '/processed_data'

with DAG(
    'nyc_taxi_pipeline',
    default_args=default_args,
    description='ETL pipeline for NYC Taxi data with Dockerized tasks',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["aieng"],
) as dag:

    # Task: Download Data
    download_data = DockerOperator(
        task_id='download_data',
        image='download_data_image',
        auto_remove=True,
        command='',
        docker_conn_id='docker_default',
        api_version='auto',
        network_mode='bridge',
        mount_tmp_dir=False,
        mounts=[
            Mount(source=HOST_DATA_DIR, target=CONTAINER_DATA_DIR, type='bind'),
        ],
        environment={
            'DATA_DIR': CONTAINER_DATA_DIR,
        },
    )

    # Task: Process Data
    process_data = DockerOperator(
        task_id='process_data',
        image='process_data_image',
        auto_remove=True,
        command='',
        docker_conn_id='docker_default',
        api_version='auto',
        network_mode='bridge',
        mount_tmp_dir=False,
        mounts=[
            Mount(source=HOST_DATA_DIR, target=CONTAINER_DATA_DIR, type='bind'),
            Mount(source=HOST_PROCESSED_DATA_DIR, target=CONTAINER_PROCESSED_DATA_DIR, type='bind'),
        ],
        environment={
            'DATA_DIR': CONTAINER_DATA_DIR,
            'PROCESSED_DATA_DIR': CONTAINER_PROCESSED_DATA_DIR,
        },
    )

    # Task: Validate Data
    validate_data = DockerOperator(
        task_id='validate_data',
        image='validate_data_image',
        auto_remove=True,
        command='',
        docker_conn_id='docker_default',
        api_version='auto',
        network_mode='bridge',
        mount_tmp_dir=False,
        mounts=[
            Mount(source=HOST_PROCESSED_DATA_DIR, target=CONTAINER_PROCESSED_DATA_DIR, type='bind'),
        ],
        environment={
            'PROCESSED_DATA_DIR': CONTAINER_PROCESSED_DATA_DIR,
        },
    )

    # Task: Create Table in PostgreSQL
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS daily_totals (
            date DATE,
            total_amount FLOAT
        );
        """,
    )

    # Task: Load Data into PostgreSQL
    load_data = DockerOperator(
        task_id='load_data',
        image='load_data_image',
        auto_remove=True,
        command='',
        docker_conn_id='docker_default',
        api_version='auto',
        network_mode='nyc_taxi_data_etl_pipeline_airflow_network',
        mount_tmp_dir=False,
        mounts=[
            Mount(source=HOST_PROCESSED_DATA_DIR, target=CONTAINER_PROCESSED_DATA_DIR, type='bind'),
        ],
        environment={
            'PROCESSED_DATA_DIR': CONTAINER_PROCESSED_DATA_DIR,
            'DB_USER': 'airflow',
            'DB_PASSWORD': 'airflow',
            'DB_HOST': 'postgres',
            'DB_PORT': '5432',
            'DB_NAME': 'airflow',
        },
    )

    # Define task dependencies
    download_data >> process_data >> validate_data >> create_table >> load_data
