from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import logging
import configparser
import os
import sys


# Read config file
config = configparser.ConfigParser()
config.read('../../config/fastapi_service_config.ini')

# Set up logging
logger = logging.getLogger(__name__)

# Adjust the path to access necessary modules and files
sys.path.append('../../../house_prices_aieng_pipelines')

# Access the model and preprocessing components
from inference_pipeline.serving_service.model.model import ModelLoader
from inference_pipeline.serving_service.model.preprocess_output import Preprocessor

# Initialize model loader with paths from config
model_loader = ModelLoader()
model = model_loader.model
model_columns = model_loader.model_columns

# Initialize the Preprocessor with model_columns and the label encoders from config
encoders_filepath = config['paths']['encoders_filepath']
preprocessor = Preprocessor(model_columns, encoders_filepath=encoders_filepath)

router = APIRouter()

class HouseData(BaseModel):
    data: dict

@router.post("/predict", response_model=dict)
async def predict(house_data: HouseData):
    try:
        input_df = pd.DataFrame([house_data.data])
        logger.info(f"Input DataFrame:\n{input_df}")

        # Preprocess the input data
        preprocessed_input = preprocessor.preprocess(input_df)
        logger.info(f"Preprocessed input columns: {preprocessed_input.columns.tolist()}")

        # Perform prediction
        prediction = model.predict(preprocessed_input.values)
        logger.info(f"Prediction successful. Predicted value: {prediction[0]}")

        return {"predicted_price": float(prediction[0])}
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
