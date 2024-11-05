from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'streaming_data_pipeline',
    default_args=default_args,
    description='Streaming Data Pipeline with Kafka and Spark Structured Streaming',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    start_producer = DockerOperator(
        task_id='start_data_producer',
        image='data_producer_image',
        auto_remove=True,
        command='python data_producer.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='streaming_data_pipeline_streaming_network',
        mount_tmp_dir=False,  # Add this line
    )

    start_processor = DockerOperator(
        task_id='start_data_processor',
        image='data_processor_image',
        auto_remove=True,
        command=(
            '--master local[*] '
            '--packages '
            'org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,'
            'org.postgresql:postgresql:42.6.0 '
            'data_processor.py'
        ),
        docker_url='unix://var/run/docker.sock',
        network_mode='streaming_data_pipeline_streaming_network',
        mount_tmp_dir=False,
    )

    # Remove the dependency if you want them to run in parallel
    # start_producer >> start_processor
