# House Prediction AI Engineering Pipeline

This project demonstrates an AI Engineering pipeline for predicting house prices using a machine learning model. It is designed to simulate the process of data ingestion from multiple sources, schema validation, data quality checks, feature registration (future step), and model training/inference.

## Project Structure

```bash
.
├── README.md                     # Project description and instructions
├── artifacts                     # Stores raw data, schema, models, and intermediate artifacts
│   ├── house_price_data.csv       # Sample house price dataset
│   ├── model_catalog              # Stores trained models and metadata
│   ├── test.csv                   # Test dataset
│   ├── test_schema.csv            # Test schema for validation (without 'SalePrice')
│   ├── train.csv                  # Train dataset
│   ├── train_schema.csv           # Train schema for validation
│   └── tmp                        # Temporary storage for label encoders, etc.
├── capabilities                   # Model catalog and related capabilities
│   └── model_catalog.py           # Handles model loading and saving
├── data_pipeline                  # Main data pipeline components
│   ├── Makefile                   # Automates pipeline steps
│   ├── combine_data_sources       # Combines multiple data sources
│   │   └── combine_raw_data.py    # Script to combine raw data from multiple sources
│   ├── features_registeration     # (Future step for feature registration)
│   ├── final_test.csv             # Final test file after pipeline
│   ├── final_train.csv            # Final train file after pipeline
│   ├── intermediate               # Intermediate files after combining data
│   │   ├── combined_test.csv      # Combined test file from multiple sources
│   │   └── combined_train.csv     # Combined train file from multiple sources
│   ├── main.py                    # Main script for running the pipeline
│   ├── quality_validation         # Quality checks for the data
│   │   └── data_quality_checks.py # Data quality validation functions
│   ├── raw_data_consumer          # Ingests data from multiple raw sources
│   │   └── raw_data_consumer.py   # Splits raw data into multiple parts
│   ├── schema_validation          # Schema validation and column reordering
│   │   └── schema_validation.py   # Validates and reorders data based on schema
│   └── utils                      # Utilities (e.g., generate schema from data)
├── inference_pipeline             # Pipeline for serving models via API
│   ├── app.py                     # FastAPI app for serving the model
│   ├── endpoints                  # API endpoints for prediction and health checks
│   └── serving_service            # Inference model loading and preprocessing logic
├── training_pipeline              # Handles training-related tasks
│   ├── feature_engineering.py     # Feature engineering during training
│   ├── model_training.py          # Training logic for the model
│   ├── utils                      # Utility scripts like model loading, visualization
└── requirements.txt               # Project dependencies
```
## Steps in the Pipeline

### 1. Data Ingestion (Raw Data Consumer)
- The `raw_data_consumer.py` simulates data ingestion from multiple sources.
- It splits the raw training and test data into two parts and stores them in `data_sources/`.

### 2. Combining Data Sources
- The `combine_raw_data.py` script combines the split datasets back into a single file.
- This simulates merging data from multiple sources into a unified dataset.

### 3. Schema Validation
- The schema is defined in `train_schema.csv` (for training data) and `test_schema.csv` (for testing data).
- The `schema_validation.py` script checks if the schema (columns and data types) of the combined data matches the expected schema.
- Missing columns and data type mismatches are flagged.

### 4. Data Quality Checks
- After schema validation, the `data_quality_checks.py` performs checks for missing values, duplicate records, and any other quality metrics.
- Any issues found are reported, ensuring data quality before model training.

### 5. Feature Registration (Future)
- This step will handle feature registration, ensuring that the model only trains on selected and validated features.

### 6. Model Training and Inference
- The `training_pipeline` handles model training using the prepared data.
- The `inference_pipeline` serves the trained model via FastAPI for real-time predictions.

## How to Run the Pipeline

### Requirements
1. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Ensure that the required raw data files (`train.csv`, `test.csv`) are placed in the `artifacts/` directory.

### Running the Pipeline

1. **Running with `make` (preferred)**:
    - A `Makefile` is provided to automate the pipeline:
    ```bash
    make all        # Runs the complete pipeline
    ```

2. **Manual Steps**:
    - Run the pipeline manually by executing the steps in `main.py`:
    ```bash
    python data_pipeline/main.py
    ```

### Expected Output

After the pipeline runs:
- Final preprocessed and validated data will be available as:
  - `final_train.csv`
  - `final_test.csv`

- Schema validation results and quality check results will be printed to the console.

## Schema Validation

- The schemas for train and test datasets are stored in `train_schema.csv` and `test_schema.csv`, respectively.
- The validation step ensures that the data conforms to these schemas before moving on to training.

## Data Quality Checks

- Missing values, duplicates, and potential anomalies are checked during the data quality validation step.
- Reports any data quality issues for further cleaning or correction.

## Inference Pipeline

- The trained model is served using FastAPI, enabling real-time predictions.
- Access API via `/predict` endpoint.

## Future Enhancements

- **Feature Registration**: Define and register relevant features before training.
- **Model Monitoring**: Add a model monitoring service to track model performance post-deployment.