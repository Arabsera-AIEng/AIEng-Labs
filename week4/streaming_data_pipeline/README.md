# Streaming Data Pipeline with Kafka, Spark, and Airflow

This project sets up an end-to-end data pipeline using **Apache Kafka** for data streaming, **Apache Spark** for processing, and **Apache Airflow** for orchestration. It leverages **Docker** for containerization, making the setup easy to replicate and deploy.

## Table of Contents
- [Introduction](#introduction)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Pipeline Overview](#pipeline-overview)
- [Docker Compose Configuration](#docker-compose-configuration)
- [Airflow DAG Pipeline](#airflow-dag-pipeline)
- [Makefile Commands](#makefile-commands)
- [Pipeline Steps Explanation](#pipeline-steps-explanation)
  - [Produce Data](#produce-data)
  - [Process Data](#process-data)
- [Running the Pipeline](#running-the-pipeline)
- [Accessing Airflow UI](#accessing-airflow-ui)
- [Cleaning Up](#cleaning-up)

## Introduction

This project demonstrates a real-time data processing pipeline by simulating streaming data using Kafka, processing it in real-time with Spark Structured Streaming, and orchestrating the workflow with Airflow. This setup is useful for scenarios requiring low-latency processing of data, such as financial transaction monitoring or live analytics.

## Technologies Used

- **Apache Kafka**: A distributed streaming platform for building real-time data pipelines.
- **Apache Spark**: Used for high-speed, fault-tolerant stream processing.
- **Apache Airflow**: Manages and orchestrates the pipeline tasks.
- **Docker**: Containers the services for ease of deployment and scaling.
- **PostgreSQL**: Stores processed data for further analysis.

## Setup and Installation

### Prerequisites
- **Docker**: Install Docker from [Docker's official website](https://www.docker.com/get-started).
- **Docker Compose**: Ensure Docker Compose is installed to manage multi-container applications.

### Instructions

1. **Clone the Repository**:

   ```
   git clone https://github.com/yourusername/streaming-data-pipeline.git
   cd streaming-data-pipeline
   ```

2. **Build Docker Images**:

   ```
   make build
   ```

3. **Set Up Services**:

   ```
   make setup
   ```

4. **Create Airflow User**:

   ```
   make create-user
   ```

## Pipeline Overview

The pipeline consists of two main tasks:

1. **Produce Data**: A Kafka producer generates simulated data and sends it to a Kafka topic.
2. **Process Data**: A Spark job consumes data from Kafka, performs transformations, and writes the results to PostgreSQL.

## Docker Compose Configuration

The `docker-compose.yaml` file defines the services required for this pipeline. Here’s the configuration:

```yaml
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"
    networks:
      - streaming_network

  kafka:
    image: wurstmeister/kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: kafka
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - streaming_network

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=streaming_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - streaming_network

  airflow-webserver:
    image: apache/airflow:2.5.1
    user: "0:0"
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/streaming_db
    depends_on:
      - postgres
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/logs:/opt/airflow/logs
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "8080:8080"
    command: webserver
    networks:
      - streaming_network

  airflow-scheduler:
    image: apache/airflow:2.5.1
    user: "0:0"
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/streaming_db
    depends_on:
      - postgres
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/logs:/opt/airflow/logs
      - /var/run/docker.sock:/var/run/docker.sock
    command: scheduler
    networks:
      - streaming_network

volumes:
  postgres_data:

networks:
  streaming_network:
    driver: bridge
```

## Services

### zookeeper

- **Image**: Uses the `wurstmeister/zookeeper` image.
- **Ports**: Exposes port `2181` to allow Kafka to communicate.
- **Networks**: Connected to `streaming_network` for internal communication.

### kafka

- **Image**: Uses the `wurstmeister/kafka` image.
- **Environment**: Configures the advertised host name and Zookeeper connection.
- **Ports**: Exposes port `9092`.
- **Volumes**: Mounts the Docker socket for internal communication.
- **Networks**: Connected to `streaming_network`.

### postgres

- **Image**: Uses the official PostgreSQL 13 image.
- **Environment Variables**: Configures the database user, password, and database name.
- **Ports**: Exposes port `5432` for database access.
- **Volumes**: Uses `postgres_data` volume for persistent data storage.
- **Networks**: Connected to `streaming_network`.

### airflow-webserver and airflow-scheduler

- **Image**: Uses the official Apache Airflow image (version 2.5.1).
- **User**: Runs as root (`0:0`) to prevent permission issues.
- **Environment Variables**: Configures Airflow to connect to the PostgreSQL database.
- **Volumes**: Mounts the `dags`, `logs`, and Docker socket for full access.
- **Ports**: The webserver exposes port `8080` for accessing the Airflow UI.
- **Networks**: Connected to `streaming_network`.

## Airflow DAG Pipeline

The Airflow DAG (`streaming_pipeline.py`) defines the workflow and dependencies between tasks:

```python
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
        network_mode='streaming_network',
    )

    start_processor = DockerOperator(
        task_id='start_data_processor',
        image='data_processor_image',
        auto_remove=True,
        command='--master local[*] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 data_processor.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='streaming_network',
    )

    start_producer >> start_processor
```

## Makefile Commands

The `Makefile` simplifies common tasks:

```makefile
# Makefile for Streaming Data Pipeline

.PHONY: build setup create-user start stop reset logs

build:
	docker build -t data_producer_image -f Dockerfile.data_producer .
	docker build -t data_processor_image -f Dockerfile.data_processor .

setup:
	docker-compose up -d

create-user:
	docker-compose run --rm airflow-webserver airflow users create \
		--username admin \
		--password admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com

start:
	docker-compose start

stop:
	docker-compose down

reset: stop
	docker volume rm streaming_data_pipeline_postgres_data

logs:
	docker-compose logs -f
```

## Pipeline Steps Explanation

### Produce Data

**Script**: `data_producer.py`

```python
import os
import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')

def get_data():
    return {'value': random.randint(0, 100)}

while True:
    data = get_data()
    producer.send('test_topic', value=json.dumps(data).encode('utf-8'))
    time.sleep(1)
```

### Process Data

**Script**: `data_processor.py`

```python
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
from pyspark.sql.types import StructType, StructField, IntegerType

spark = SparkSession.builder.appName("KafkaSparkStreaming").getOrCreate()

schema = StructType([StructField("value", IntegerType())])

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "test_topic") \
    .load()

df.selectExpr("CAST(value AS STRING)") \
  .groupBy() \
  .agg(avg("value").alias("average")) \
  .writeStream \
  .format("console") \
  .start() \
  .awaitTermination()
```

## Running the Pipeline

To run the pipeline:

1. **Build Docker Images**:

   ```
   make build
   ```

2. **Start Services**:

   ```
   make setup
   ```

3. **Access Airflow UI** at [http://localhost:8080](http://localhost:8080).

## Accessing Airflow UI

- **URL**: [http://localhost:8080](http://localhost:8080)
- **Default Credentials**:
  - **Username**: `admin`
  - **Password**: `admin`

## Cleaning Up

To stop services and clean up:

```
make reset
```
