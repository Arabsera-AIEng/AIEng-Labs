from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics import mean_squared_error

router = APIRouter()
logger = logging.getLogger(__name__)


# Define the class for incoming data format
class ActualPriceData(BaseModel):
    features: dict  # Input features as a dictionary
    predicted_price: float  # The predicted price of the house
    actual_price: float  # The actual sale price of the house
    timestamp: str  # Timestamp when the data was collected/submitted


# Define the CSV file path
CSV_FILE_PATH = "/Users/amenshawy/Documents/teaching/arabsera/ai_engineering_2024/week2/house_prices_aieng_pipelines/artifacts/house_price_data.csv"


# Function to calculate Root Mean Squared Logarithmic Error (RMSLE)
def rmsle(y, y_pred):
    return np.sqrt(mean_squared_error(y, y_pred))


@router.post("/submit_actual", response_model=dict)
async def submit_actual(actual_data: ActualPriceData):
    """
    Submit the actual sale price of the house.
    Maintains a moving window of 1 hour worth of data and calculates RMSLE.
    """
    try:
        logger.info("Received actual price submission request.")

        # Convert timestamp from string to datetime
        actual_data.timestamp = datetime.fromisoformat(actual_data.timestamp)

        # Extract features and prices
        features = actual_data.features
        predicted_price = actual_data.predicted_price
        actual_price = actual_data.actual_price

        # Create a row for the CSV with the features, predicted price, actual price, and timestamp
        csv_row = pd.DataFrame([{**features, "predicted_price": predicted_price, "actual_price": actual_price,
                                 "timestamp": actual_data.timestamp}])

        # Check if the CSV file exists
        file_exists = os.path.isfile(CSV_FILE_PATH)

        # Read existing data if the file exists
        if file_exists:
            data = pd.read_csv(CSV_FILE_PATH)
            # Convert the 'timestamp' column to datetime
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            # Filter the data to keep only rows within the last 1 hour
            one_hour_ago = actual_data.timestamp - timedelta(hours=1)
            data = data[data['timestamp'] >= one_hour_ago]
        else:
            # Create an empty DataFrame with the necessary columns if file doesn't exist
            data = pd.DataFrame(columns=[*features.keys(), 'predicted_price', 'actual_price', 'timestamp'])

        # Add the new row to the DataFrame using pd.concat()
        data = pd.concat([data, csv_row], ignore_index=True)

        # Save the filtered data back to the CSV file
        data.to_csv(CSV_FILE_PATH, index=False)

        # Calculate RMSLE on the existing data within the last 1 hour
        if len(data) > 0:
            rmsle_value = rmsle(data['actual_price'].values, data['predicted_price'].values)
        else:
            rmsle_value = None

        logger.info(f"Data saved successfully to {CSV_FILE_PATH}.")
        logger.info(f"Calculated RMSLE: {rmsle_value}")

        # Return a confirmation message with RMSLE metric
        return {
            "message": "Information received and saved successfully.",
            "rmsle": rmsle_value
        }
    except Exception as e:
        logger.error(f"Error processing actual price submission: {e}")
        raise HTTPException(status_code=400, detail="Failed to process actual price submission.")
