# tests/test_app.py

import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
import json
import logging

from app import app

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TestClient(app)

# Sample test data based on the provided CSV data
sample_input_data = {
    "MSSubClass": 20,
    "MSZoning": "RH",
    "LotFrontage": 80.0,
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
    "MasVnrArea": 0.0,
    "ExterQual": "TA",
    "ExterCond": "TA",
    "Foundation": "CBlock",
    "BsmtQual": "TA",
    "BsmtCond": "TA",
    "BsmtExposure": "No",
    "BsmtFinType1": "Rec",
    "BsmtFinSF1": 468.0,
    "BsmtFinType2": "LwQ",
    "BsmtFinSF2": 144.0,
    "BsmtUnfSF": 270.0,
    "TotalBsmtSF": 882.0,
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
    "GarageYrBlt": 1961.0,
    "GarageFinish": "Unf",
    "GarageCars": 1.0,
    "GarageArea": 730.0,
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

class TestAPI:
    """Test suite for the House Price Prediction API."""

    def test_health_check(self):
        """Test the /health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_version(self):
        """Test the /version endpoint."""
        response = client.get("/api/version")
        assert response.status_code == 200
        json_response = response.json()
        assert "model_version" in json_response
        assert "algorithm" in json_response
        assert "project_name" in json_response
        assert "rmse" in json_response

    def test_predict_success(self):
        """Test the /predict endpoint with valid data."""
        response = client.post(
            "/api/predict",
            json={"data": sample_input_data}
        )
        assert response.status_code == 200
        json_response = response.json()
        assert "predicted_price" in json_response
        assert isinstance(json_response["predicted_price"], float)
        assert json_response["predicted_price"] > 0  # Predicted price should be positive

    def test_predict_missing_fields(self):
        """Test the /predict endpoint with missing required fields."""
        incomplete_data = sample_input_data.copy()
        incomplete_data.pop("GrLivArea")  # Remove a required field
        response = client.post(
            "/api/predict",
            json={"data": incomplete_data}
        )
        assert response.status_code == 400
        json_response = response.json()
        assert "detail" in json_response

    def test_predict_invalid_data(self):
        """Test the /predict endpoint with invalid data types."""
        invalid_data = sample_input_data.copy()
        invalid_data["GrLivArea"] = "invalid"  # Invalid data type
        response = client.post(
            "/api/predict",
            json={"data": invalid_data}
        )
        assert response.status_code == 400
        json_response = response.json()
        assert "detail" in json_response

    def test_predict_extra_fields(self):
        """Test the /predict endpoint with extra fields not used by the model."""
        extra_data = sample_input_data.copy()
        extra_data["ExtraField"] = "ExtraValue"  # Add an extra field
        response = client.post(
            "/api/predict",
            json={"data": extra_data}
        )
        assert response.status_code == 200
        json_response = response.json()
        assert "predicted_price" in json_response

    def test_predict_empty_payload(self):
        """Test the /predict endpoint with an empty payload."""
        response = client.post(
            "/api/predict",
            json={}
        )
        assert response.status_code == 422  # Unprocessable Entity
        json_response = response.json()
        assert "detail" in json_response

    def test_predict_no_payload(self):
        """Test the /predict endpoint with no payload."""
        response = client.post("/api/predict")
        assert response.status_code == 422  # Unprocessable Entity
        json_response = response.json()
        assert "detail" in json_response
