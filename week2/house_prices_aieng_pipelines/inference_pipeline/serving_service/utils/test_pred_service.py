import pandas as pd
import numpy as np
import logging
import sys
import os

# Adjust the path to access necessary modules and files
sys.path.append('/Users/amenshawy/Documents/teaching/arabsera/ai_engineering_2024/week2/house_prices_aieng_pipelines')


import pickle
from scipy.special import boxcox1p
from scipy.stats import skew
from sklearn.preprocessing import LabelEncoder
from inference_pipeline.serving_service.model.model import ModelLoader
from inference_pipeline.serving_service.model.preprocess_output import Preprocessor


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up paths and other configuration
sys.path.append('/Users/amenshawy/Documents/teaching/arabsera/ai_engineering_2024/week2/house_prices_aieng_pipelines')
ENCODERS_FILEPATH = '/tmp/label_encoders.pkl'

# Load the model and columns
print("Loading model and preprocessing components...")
model_loader = ModelLoader()
model = model_loader.model
model_columns = model_loader.model_columns
print(f"Model loaded successfully. Model columns: {model_columns}")

# Initialize the Preprocessor with model_columns and label encoders
preprocessor = Preprocessor(model_columns, encoders_filepath=ENCODERS_FILEPATH)
print("Preprocessor initialized with model columns and label encoders.")

# Define a sample record for testing
sample_record = {
    "Id": 1461,
    "MSSubClass": 20,
    "MSZoning": "RH",
    "LotFrontage": 80,
    "LotArea": 11622,
    "Street": "Pave",
    "Alley": None,
    "LotShape": "Reg",
    "LandContour": "Lvl",
    "Utilities": "AllPub",
    "LotConfig": "Inside",
    "LandSlope": "Gtl",
    "Neighborhood": "NAmes",
    "Condition1": "Feedr",
    "Condition2": "Norm",
    "BldgType": "1Fam",
    "HouseStyle": "1Story",
    "OverallQual": 5,
    "OverallCond": 6,
    "YearBuilt": 1961,
    "YearRemodAdd": 1961,
    "RoofStyle": "Gable",
    "RoofMatl": "CompShg",
    "Exterior1st": "VinylSd",
    "Exterior2nd": "VinylSd",
    "MasVnrType": None,
    "MasVnrArea": 0,
    "ExterQual": "TA",
    "ExterCond": "TA",
    "Foundation": "CBlock",
    "BsmtQual": "TA",
    "BsmtCond": "TA",
    "BsmtExposure": "No",
    "BsmtFinType1": "Rec",
    "BsmtFinSF1": 468,
    "BsmtFinType2": "LwQ",
    "BsmtFinSF2": 144,
    "BsmtUnfSF": 270,
    "TotalBsmtSF": 882,
    "Heating": "GasA",
    "HeatingQC": "TA",
    "CentralAir": "Y",
    "Electrical": "SBrkr",
    "1stFlrSF": 896,
    "2ndFlrSF": 0,
    "LowQualFinSF": 0,
    "GrLivArea": 896,
    "BsmtFullBath": 0,
    "BsmtHalfBath": 0,
    "FullBath": 1,
    "HalfBath": 0,
    "BedroomAbvGr": 2,
    "KitchenAbvGr": 1,
    "KitchenQual": "TA",
    "TotRmsAbvGrd": 5,
    "Functional": "Typ",
    "Fireplaces": 0,
    "FireplaceQu": None,
    "GarageType": "Attchd",
    "GarageYrBlt": 1961,
    "GarageFinish": "Unf",
    "GarageCars": 1,
    "GarageArea": 730,
    "GarageQual": "TA",
    "GarageCond": "TA",
    "PavedDrive": "Y",
    "WoodDeckSF": 140,
    "OpenPorchSF": 0,
    "EnclosedPorch": 0,
    "3SsnPorch": 0,
    "ScreenPorch": 120,
    "PoolArea": 0,
    "PoolQC": None,
    "Fence": "MnPrv",
    "MiscFeature": None,
    "MiscVal": 0,
    "MoSold": 6,
    "YrSold": 2010,
    "SaleType": "WD",
    "SaleCondition": "Normal"
}

# Create a DataFrame with the sample record
print("Creating DataFrame from sample record...")
input_df = pd.DataFrame([sample_record])
print(f"Initial DataFrame:\n{input_df}")

# Check for missing columns
missing_cols = set(model_columns) - set(input_df.columns)
if missing_cols:
    print(f"Missing columns detected: {missing_cols}")

# Align the DataFrame columns with the model columns (fill missing with default)
# input_df = input_df.reindex(columns=model_columns, fill_value=0)
# print(f"DataFrame columns after reindexing:\n{input_df.columns.tolist()}")

# Perform preprocessing
print("Performing preprocessing on the input data...")
preprocessed_input = preprocessor.preprocess(input_df)
print(f"Preprocessed input:\n{preprocessed_input}")

preprocessed_input = preprocessed_input.reindex(columns=model_columns, fill_value=0)
print(f"DataFrame columns after reindexing:\n{preprocessed_input.columns.tolist()}")

# Check if there are any missing columns after preprocessing
missing_after_preprocessing = set(model_columns) - set(preprocessed_input.columns)
if missing_after_preprocessing:
    print(f"Missing columns after preprocessing: {missing_after_preprocessing}")
else:
    print("All required columns are present after preprocessing.")

# Perform prediction
print("Performing prediction...")
prediction = model.predict(preprocessed_input.values)
print(f"Prediction successful. Predicted value: {prediction[0]}")

print(f"Predicted house price: {float(prediction[0])}")

