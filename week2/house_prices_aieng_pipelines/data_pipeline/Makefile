# Makefile for Data Pipeline

.PHONY: all split combine validate quality_check run

# Get the absolute path of the config file
CONFIG_PATH := $(shell realpath ../config/config.ini)

# Default target: Run the entire pipeline
all: split combine validate quality_check run

# Step 1: Split the data into multiple sources
split:
	python -m raw_data_consumer.raw_data_consumer --config $(CONFIG_PATH)

# Step 2: Combine data parts into a single dataset
combine:
	python -m combine_data_sources.combine_raw_data --config $(CONFIG_PATH)

# Step 3: Validate and reorder schema
validate:
	python -m schema_validation.schema_validation --config $(CONFIG_PATH)

# Step 4: Perform data quality checks
quality_check:
	python -m quality_validation.data_quality_checks --config $(CONFIG_PATH)

# Step 5: Run the main pipeline script
run:
	python main.py --config $(CONFIG_PATH)