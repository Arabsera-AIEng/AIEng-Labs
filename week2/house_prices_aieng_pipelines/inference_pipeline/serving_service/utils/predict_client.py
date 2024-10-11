# predict_client.py

import requests
import json

def main():
    # API endpoint URL
    url = "http://localhost:8000/api/predict"

    # Sample input data
    sample_input_data = {
        "data": {
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
    }

    # Headers for the POST request
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Send POST request to the API
        response = requests.post(url, headers=headers, data=json.dumps(sample_input_data))

        print(response.json())

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            predicted_price = result.get("predicted_price", None)
            if predicted_price is not None:
                print(f"Predicted House Price: ${predicted_price:,.2f}")
            else:
                print("Prediction failed. No predicted price returned.")
        else:
            print(f"Request failed with status code: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    main()
