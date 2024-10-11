import argparse
from raw_data_consumer.raw_data_consumer import RawDataConsumer
from combine_data_sources.combine_raw_data import DataCombiner
from schema_validation.schema_validation import SchemaValidator
from quality_validation.data_quality_checks import DataQualityChecker
import pandas as pd

def main():
    # Parse the configuration file path from command-line arguments
    parser = argparse.ArgumentParser(description="Main Pipeline Script")
    parser.add_argument('--config', required=True, help="Path to the configuration file")
    args = parser.parse_args()

    # Step 1: Split raw data into multiple sources
    data_consumer = RawDataConsumer(config_path=args.config)
    data_consumer.split_data_sources()

    # Step 2: Combine split data parts
    data_combiner = DataCombiner(config_path=args.config)
    data_combiner.combine_data_parts('train_part1.csv', 'train_part2.csv', 'combined_train.csv')
    data_combiner.combine_data_parts('test_part1.csv', 'test_part2.csv', 'combined_test.csv')

    # Step 3: Validate schema of combined data
    schema_validator = SchemaValidator(config_path=args.config)
    combined_train = pd.read_csv(schema_validator.combined_train_path)
    combined_test = pd.read_csv(schema_validator.combined_test_path)

    train_schema_validation = schema_validator.validate_schema(combined_train)
    test_schema_validation = schema_validator.validate_schema(combined_test, exclude_columns=['SalePrice'])

    print(f"Train Schema Validation: {train_schema_validation}")
    print(f"Test Schema Validation: {test_schema_validation}")

    # Reorder columns based on schema
    combined_train = schema_validator.reorder_columns(combined_train)
    combined_test = schema_validator.reorder_columns(combined_test, exclude_columns=['SalePrice'])

    # Step 4: Perform data quality checks
    train_quality_checker = DataQualityChecker(combined_train, config_path=args.config)
    test_quality_checker = DataQualityChecker(combined_test, config_path=args.config)

    train_quality_checker.run_checks()
    test_quality_checker.run_checks()

    # Step 5: Save the final validated and quality-checked data
    combined_train.to_csv(schema_validator.final_train_path, index=False)
    combined_test.to_csv(schema_validator.final_test_path, index=False)

    print("Final training and testing files created successfully.")

if __name__ == "__main__":
    main()