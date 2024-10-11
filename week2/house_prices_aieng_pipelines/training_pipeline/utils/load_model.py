from capabilities.model_catalog import ModelCatalog
import pandas as pd
import numpy as np


def main():
    # Create an instance of ModelCatalog
    model_catalog = ModelCatalog()

    # Specify the model name
    model_name = 'house_price_stacked_model'

    # Load the model, model card, and model columns
    model, model_card, model_columns = model_catalog.load_model(model_name)

    print("Loaded Model Card:")
    for key, value in model_card.items():
        print(f"{key}: {value}")

    # Prepare a sample input row
    # For demonstration, we'll use a sample from the test dataset
    data_loader = DataLoader()
    _, test = data_loader.load_data()

    # Select a sample row
    sample_input = test.iloc[[2]]  # Adjust index as needed

    # Preprocess the sample input
    preprocessed_input = model_catalog.preprocess_input(sample_input, model_columns)

    # Perform inference
    prediction = model.predict(preprocessed_input.values)

    # Since the target variable was log-transformed, we need to inverse transform
    predicted_price = np.expm1(prediction)
    print(f"Predicted House Price: {predicted_price[0]}")


if __name__ == '__main__':
    from training_pipeline.data_consumer.data_loader import DataLoader

    main()
