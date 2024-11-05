# NYC Taxi Data ETL Pipeline with Airflow and Docker

This project demonstrates an end-to-end Extract, Transform, Load (ETL) pipeline for processing New York City taxi data using **Apache Airflow**, **Docker**, and **Docker Compose**. The pipeline automates the workflow of downloading, processing, validating, and loading data into a PostgreSQL database. Each step is containerized with Docker, ensuring consistency and portability across different environments

## Table of Contents
- [Introduction](#introduction)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Pipeline Overview](#pipeline-overview)
- [Docker Compose Configuration](#docker-compose-configuration)
- [Airflow DAG Pipeline](#airflow-dag-pipeline)
- [Makefile Commands](#makefile-commands)
- [Pipeline Steps Explanation](#pipeline-steps-explanation)
  - [Download Data](#download-data)
  - [Process Data](#process-data)
  - [Validate Data](#validate-data)
  - [Load Data](#load-data)
- [Great Expectations Library](#great-expectations-library)
- [Running the Pipeline](#running-the-pipeline)
- [Accessing Airflow UI](#accessing-airflow-ui)
- [Cleaning Up](#cleaning-up)

## Introduction

The goal of this project is to set up a data pipeline that processes NYC taxi data. The pipeline automates the extraction of data from an external source, transforms the data to a suitable format, validates the data quality, and loads it into a PostgreSQL database for further analysis. By leveraging Docker and Airflow, the pipeline ensures reproducibility, scalability, and ease of maintenance

## Technologies Used

- **Apache Airflow**: A platform to programmatically author, schedule, and monitor workflows
- **Docker**: A tool designed to make it easier to create, deploy, and run applications by using containers
- **Docker Compose**: A tool for defining and running multi-container Docker applications
- **Python**: The programming language used for scripting the pipeline steps
- **Pandas**: A Python library for data manipulation and analysis
- **SQLAlchemy**: A Python SQL toolkit and Object-Relational Mapping (ORM) library
- **Great Expectations**: A Python library for data validation
- **PostgreSQL**: An open-source relational database system

## Prerequisites

- **Docker Desktop**: Install Docker Desktop for your operating system from [Docker's official website](https://www.docker.com/products/docker-desktop)
- **Basic Knowledge of Python**: Understanding Python will help in comprehending the scripts used in the pipeline
- **No Prior Knowledge of Airflow or Docker Compose Required**: This README provides detailed explanations of these technologies

## Setup and Installation

Follow these steps to set up and run the project:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/nyc-taxi-pipeline.git
   cd nyc-taxi-pipeline
   ```
   
2. **Build Docker Images**:
   Use the provided Makefile to build all the Docker images required for the pipeline steps
   
   ```bash
   make build
   ```

3. **Set Up and Start Services**:
   Initialize Airflow and start all services using Docker Compose

   ```bash
   make setup
   ```

## Pipeline Overview
The pipeline consists of the following steps:

1. Download Data: Downloads NYC taxi data for specified months
2. Process Data: Transforms the raw data into a structured format
3. Validate Data: Ensures data quality using Great Expectations
4. Create Table: Creates a table in PostgreSQL to store the data
5. Load Data: Loads the validated data into the PostgreSQL database. 

Each step is containerized using Docker and orchestrated by an Airflow DAG (Directed Acyclic Graph)

## Docker Compose Configuration
The `docker-compose.yaml` file defines the services required for the pipeline. Here's the configuration:

```yaml
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - airflow_network

  webserver:
    image: apache/airflow:2.5.1
    user: "0:0"
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW_EXTRA_PIP_PACKAGES=apache-airflow-providers-postgres==3.3.0 'SQLAlchemy<2.0' apache-airflow-providers-docker docker
    depends_on:
      - postgres
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./data:/data
      - ./processed_data:/processed_data
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "8080:8080"
    command: webserver
    networks:
      - airflow_network

  scheduler:
    image: apache/airflow:2.5.1
    user: "0:0"
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW_EXTRA_PIP_PACKAGES=apache-airflow-providers-postgres==3.3.0 'SQLAlchemy<2.0' apache-airflow-providers-docker docker
    depends_on:
      - postgres
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./data:/data
      - ./processed_data:/processed_data
      - /var/run/docker.sock:/var/run/docker.sock
    command: scheduler
    networks:
      - airflow_network

volumes:
  postgres_data:

networks:
  airflow_network:
    driver: bridge
```

## Services

### postgres

- **Image**: Uses the official PostgreSQL 13 image
- **Environment Variables**:
  - `POSTGRES_USER`: Username for the database (set to `airflow`)
  - `POSTGRES_PASSWORD`: Password for the database (set to `airflow`)
  - `POSTGRES_DB`: Database name (set to `airflow`)
- **Ports**: Exposes port `5432` to the host machine
- **Volumes**: Persists data using the `postgres_data` volume
- **Networks**: Connected to `airflow_network` for inter-service communication

### webserver

- **Image**: Uses the official Apache Airflow image, version 2.5.1
- **User**: Runs as root (`0:0`) to avoid permission issues
- **Environment Variables**:
  - `AIRFLOW__CORE__LOAD_EXAMPLES`: Disables loading of example DAGs
  - `AIRFLOW__CORE__EXECUTOR`: Sets the executor to `LocalExecutor`
  - `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN`: Connection string to the PostgreSQL database
  - `AIRFLOW_EXTRA_PIP_PACKAGES`: Installs additional Python packages required for the pipeline
- **Depends On**: Ensures that the `postgres` service starts before the `webserver`
- **Volumes**:
  - Mounts the `dags`, `logs`, `data`, and `processed_data` directories
  - Mounts the Docker socket (`/var/run/docker.sock`) to allow the DockerOperator to run Docker containers
- **Ports**: Exposes port `8080` for accessing the Airflow web interface
- **Command**: Runs the Airflow webserver
- **Networks**: Connected to `airflow_network`

### scheduler

- **Configuration**: Similar to the `webserver` service
- **Command**: Runs the Airflow scheduler to manage task execution

## Volumes

- **postgres_data**: A Docker volume used to persist PostgreSQL data

## Networks

- **airflow_network**: A bridge network that allows the services to communicate using service names

## Airflow DAG Pipeline
The Airflow DAG (`nyc_taxi_pipeline.py`) defines the workflow and dependencies between tasks

```python
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
HOST_DATA_DIR = os.path.abspath('data')
HOST_PROCESSED_DATA_DIR = os.path.abspath('processed_data')

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
        network_mode='airflow_airflow_network',
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
```

## DAG Definition

- **DAG**: Defines a Directed Acyclic Graph named `nyc_taxi_pipeline`
- **default_args**: Specifies default parameters for tasks, such as the owner, retries, and retry delay
- **schedule_interval**: Set to `None` to disable scheduled runs; the DAG must be triggered manually
- **start_date**: The date from which the DAG is valid
- **catchup**: Set to `False` to prevent Airflow from running past scheduled runs when starting the DAG
- **tags**: Used for categorizing and filtering in the Airflow UI

## Tasks

### download_data

- **Operator**: `DockerOperator` that runs a Docker container using the image `download_data_image`
- **Mounts**: Binds the host directory `data` to the container directory `/data`
- **Environment Variables**: Passes `DATA_DIR` environment variable to the container
- **network_mode**: Set to `'bridge'` for network isolation

### process_data

- **Operator**: `DockerOperator` that uses `process_data_image`
- **Mounts**: Binds both `data` and `processed_data` directories to the container
- **Environment Variables**: Passes `DATA_DIR` and `PROCESSED_DATA_DIR` to the container

### validate_data

- **Operator**: `DockerOperator` that uses `validate_data_image`
- **Mounts**: Binds `processed_data` directory
- **Environment Variables**: Passes `PROCESSED_DATA_DIR`

### create_table

- **Operator**: `PostgresOperator` to execute SQL commands against the PostgreSQL database
- **postgres_conn_id**: Uses the Airflow connection named `postgres_default`
- **SQL Query**: Creates the `daily_totals` table if it doesn't exist

### load_data

- **Operator**: `DockerOperator` that uses `load_data_image`
- **network_mode**: Set to `'airflow_airflow_network'` to connect to the same network as the PostgreSQL service
- **Environment Variables**: Passes database connection parameters and `PROCESSED_DATA_DIR`
- **Explanation**: This task connects to the PostgreSQL database to load data

## Task Dependencies

The pipeline follows a linear sequence of task dependencies:

- `download_data` → `process_data` → `validate_data` → `create_table` → `load_data`

Each task performs a specific function within the ETL process, ensuring a structured flow for data processing and storage


## Makefile Commands
The `Makefile` simplifies common tasks such as building images and managing services

```makefile
# Makefile for Airflow Pipeline Management

# Variables
COMPOSE_FILE=docker-compose.yaml
DOCKER_COMPOSE=docker-compose -f $(COMPOSE_FILE)
AIRFLOW_CMD=$(DOCKER_COMPOSE) run --rm webserver

# Targets
.PHONY: help build start init create-user stop clean logs setup reset

help: ## Display available commands
	@echo "Airflow Pipeline Management Makefile"
	@echo
	@echo "Available commands:"
	@echo "  make build         Build Docker images for the pipeline steps"
	@echo "  make start         Start the Airflow pipeline services"
	@echo "  make init          Initialize the Airflow database"
	@echo "  make create-user   Create an Airflow admin user"
	@echo "  make stop          Stop the Airflow pipeline services"
	@echo "  make clean         Remove all data volumes"
	@echo "  make logs          Tail the logs of all running services"
	@echo "  make setup         Run full setup from building images to creating user"
	@echo "  make reset         Stop services and clean up all volumes"

build: ## Build Docker images for all pipeline steps
	docker build -t download_data_image ./steps/download_data
	docker build -t process_data_image ./steps/process_data
	docker build -t validate_data_image ./steps/validate_data
	docker build -t load_data_image ./steps/load_data

start: ## Start Airflow and PostgreSQL services
	$(DOCKER_COMPOSE) up -d

init: ## Initialize the Airflow database
	$(AIRFLOW_CMD) airflow db init

create-user: ## Create an Airflow admin user
	$(AIRFLOW_CMD) airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com

stop: ## Stop all running Airflow services
	$(DOCKER_COMPOSE) down

clean: stop ## Stop services and remove data volumes
	docker volume rm airflow_postgres_data

logs: ## Tail logs for all services
	$(DOCKER_COMPOSE) logs -f

setup: start init create-user start ## Full setup from building images to creating user

reset: stop clean ## Stop services and clean up all volumes
```

# Airflow Pipeline Management Makefile

This Makefile provides commands to manage the Airflow pipeline, including starting services, initializing the Airflow database, and managing logs

## Variables

- **COMPOSE_FILE**: Specifies the Docker Compose file (`docker-compose.yaml`)
- **DOCKER_COMPOSE**: Shortcut for the `docker-compose` command
- **AIRFLOW_CMD**: Command to run Airflow commands inside the `webserver` container

## Targets

- **help**: Displays available commands for managing the pipeline
- **build**: Builds Docker images for each pipeline step (`download_data`, `process_data`, `validate_data`, `load_data`)
- **start**: Starts the services defined in `docker-compose.yaml` (Airflow and PostgreSQL)
- **init**: Initializes the Airflow database
- **create-user**: Creates an admin user for Airflow with the username `admin` and email `admin@example.com`
- **stop**: Stops all running Airflow and PostgreSQL services
- **clean**: Removes data volumes to clean up persisted data, ensuring a fresh start
- **logs**: Tails logs for all services, allowing for real-time monitoring of service activity
- **setup**: Runs a full setup process, including starting services, initializing Airflow, and creating a user
- **reset**: Stops services and removes all data volumes, effectively resetting the environment

## Usage

To execute a command, use the following syntax:
```bash
make <command>
```

### Available Commands

- `make build` - Build Docker images for the pipeline steps
- `make start` - Start the Airflow pipeline services
- `make init` - Initialize the Airflow database
- `make create-user` - Create an Airflow admin user
- `make stop` - Stop the Airflow pipeline services
- `make clean` - Remove all data volumes to reset the environment
- `make logs` - Tail logs for all running services
- `make setup` - Run a full setup, starting from building images to creating a user
- `make reset` - Stop services and clean up all volumes for a fresh start

This Makefile streamlines Airflow pipeline management, simplifying the setup, maintenance, and cleanup processes

# Pipeline Steps Explanation
## Download Data
**Script**: `download_data.py`

```python
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

if __name__ == '__main__':
    download_data()
```

- **Purpose**: 
  - Downloads NYC taxi data for specified months

- **Environment Variable**: 
  - `DATA_DIR`: Specifies the directory where data will be saved

- **Process**:
  - Checks if the `DATA_DIR` directory exists; if not, it creates it
  - Iterates over a list of months to download the corresponding data
  - For each month:
    - Checks if the file already exists in `DATA_DIR` to avoid re-downloading
    - Uses `curl` to download the `.parquet` files from the data source

## Process Data
**Script**: `process_data.py`

```python
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
```


- **Purpose**: 
  - Transforms raw data into a structured format suitable for analysis

- **Environment Variables**:
  - `DATA_DIR`: Directory containing raw data
  - `PROCESSED_DATA_DIR`: Directory to save processed data

- **Process**:
  - Reads `.parquet` files using Pandas
  - Converts pickup datetime to a date format
  - Aggregates total amounts per day
  - Saves the transformed data as `.csv` files in the `PROCESSED_DATA_DIR`
  

## Validate Data
**Script**: `validate_data.py`

```python
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

    for month in months:
        file_path = os.path.join(processed_data_dir, f'processed_data_{month}.csv')

        if not os.path.exists(file_path):
            logger.error(f'Processed data file {file_path} does not exist.')
            continue

        df = pd.read_csv(file_path)
        context = gx.get_context()
        suite = context.create_expectation_suite(f"validation_suite_{month}", overwrite_existing=True)

        # Define Expectations
        suite.add_expectation(gx.expect_column_to_exist("date"))
        suite.add_expectation(gx.expect_column_to_exist("total_amount"))
        suite.add_expectation(gx.expect_column_values_to_be_dateutil_parseable("date"))
        suite.add_expectation(gx.expect_column_values_to_be_between("total_amount", min_value=0))

        # Validate Data
        batch = gx.from_pandas(df)
        validation_result = context.run_validation_operator(
            "action_list_operator",
            assets_to_validate=[batch],
            run_id=f"validation_{month}",
            expectation_suite_name=suite.expectation_suite_name,
        )

        if validation_result["success"]:
            logger.info(f'Data validation passed for {month}')
        else:
            logger.error(f'Data validation failed for {month}')
            raise ValueError(f'Data validation failed for {month}')

if __name__ == '__main__':
    validate_data()
```

- **Purpose**: 
  - Validates the processed data to ensure data quality before loading

- **Great Expectations**:
  - **Expectation Suite**: A collection of data quality expectations applied to the data
  - **Expectations Defined**:
    - Column `date` exists
    - Column `total_amount` exists
    - Values in `date` are parseable as dates
    - Values in `total_amount` are greater than or equal to zero

- **Process**:
  - Reads the processed `.csv` files
  - Creates an expectation suite for each month
  - Runs validations and checks if all expectations are met
  - Raises an error if validation fails to prevent loading invalid data
## Load Data
**Script**: `load_data.py`

```python
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
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'airflow')

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
```

- **Purpose**: 
  - Loads the validated data into the PostgreSQL database

- **Environment Variables**:
  - Database connection parameters (e.g., user, password, host, port, database name)

- **Process**:
  - Reads the processed `.csv` files
  - Connects to the PostgreSQL database using SQLAlchemy
  - Appends data to the `daily_totals` table
  - Handles exceptions and logs any errors during the loading process

# Running the Pipeline

Follow these steps to run the pipeline:

- **Build Docker Images**:
  
  ```bash
  make build
  ```

- **Set Up Services**:
  
  ```bash
  make setup
  ```

- **Access Airflow UI**:
  - Open your web browser and navigate to [http://localhost:8080](http://localhost:8080)
  - Log in with:
    - **Username**: `admin`
    - **Password**: `admin`

- **Trigger the DAG**:
  - In the Airflow UI, find `nyc_taxi_pipeline`
  - Turn on the DAG by toggling the switch
  - Trigger the DAG by clicking on the play button

- **Monitor the Pipeline**:
  - Use the **Graph** view in Airflow to track task progress
  - Click on individual tasks to view logs and details

## Accessing Airflow UI

- **URL**: [http://localhost:8080](http://localhost:8080)
- **Default Credentials**:
  - **Username**: `admin`
  - **Password**: `admin`

The Airflow UI allows you to:
  - Monitor task executions
  - View logs and task statuses
  - Manage DAGs and schedules

## Cleaning Up

To stop services and clean up data volumes:

```bash
make reset
```

This command will:
  - Stop all running services
  - Remove the PostgreSQL data volume (`airflow_postgres_data`), effectively deleting all persisted data
