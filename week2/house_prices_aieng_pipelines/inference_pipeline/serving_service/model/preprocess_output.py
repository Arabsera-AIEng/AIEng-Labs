import pandas as pd
import numpy as np
from scipy.special import boxcox1p
from scipy.stats import skew
import logging
import pickle
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

class Preprocessor:
    """
    Preprocessor class to handle data preprocessing during inference.
    """

    def __init__(self, model_columns, encoders_filepath=None):
        self.model_columns = model_columns
        self.label_encoders = {}
        self.cols_to_encode = ('FireplaceQu', 'BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond',
                               'ExterQual', 'ExterCond', 'HeatingQC', 'PoolQC', 'KitchenQual',
                               'BsmtFinType1', 'BsmtFinType2', 'Functional', 'Fence', 'BsmtExposure',
                               'GarageFinish', 'LandSlope', 'LotShape', 'PavedDrive', 'Street',
                               'Alley', 'CentralAir', 'MSSubClass', 'OverallCond', 'YrSold', 'MoSold')
        # Load the label encoders if a filepath is provided
        if encoders_filepath:
            self.load_label_encoders(encoders_filepath)

    def preprocess(self, data):
        """
        Preprocess the input data.

        Parameters:
        - data: pandas DataFrame, the input data to preprocess

        Returns:
        - data: pandas DataFrame, the preprocessed input data
        """
        logger.info(f"Initial data columns: {data.columns.tolist()}")

        # Handle missing data and log the intermediate output
        data = self._handle_missing_data(data)
        logger.info(f"Data columns after handling missing values: {data.columns.tolist()}")

        # Transform features and log the intermediate output
        data = self._transform_features(data)
        logger.info(f"Data columns after transforming features: {data.columns.tolist()}")

        # Apply label encoding and log the intermediate output
        data = self._label_encoding(data)
        logger.info(f"Data columns after label encoding: {data.columns.tolist()}")

        # Create new features and log the intermediate output
        data['TotalSF'] = data['TotalBsmtSF'] + data['1stFlrSF'] + data['2ndFlrSF']
        logger.info(f"Data columns after creating new features (TotalSF added): {data.columns.tolist()}")

        # Handle skewed features and log the intermediate output
        data = self._handle_skewed_features(data)
        logger.info(f"Data columns after handling skewed features: {data.columns.tolist()}")

        # One-Hot Encoding with pd.get_dummies and log the intermediate output
        data = pd.get_dummies(data)
        logger.info(f"Data columns after one-hot encoding: {data.columns.tolist()}")

        # Align the data with the model columns by reindexing
        missing_before_reindex = set(self.model_columns) - set(data.columns)
        logger.info(f"Missing columns before reindexing: {missing_before_reindex}")

        data = data.reindex(columns=self.model_columns, fill_value=0)

        # Log missing columns after reindexing
        missing_after_reindex = set(self.model_columns) - set(data.columns)
        logger.info(f"Missing columns after reindexing: {missing_after_reindex}")

        logger.info(f"Final data shape: {data.shape}")
        logger.info(f"Final columns in preprocessed data: {data.columns.tolist()}")

        return data

    def _handle_missing_data(self, data):
        """
        Handle missing data as per the logic defined during training.
        """
        logger.info(f"Handling missing data for columns: {data.columns.tolist()}")

        # Implement missing data handling as in your training pipeline
        data["PoolQC"] = data["PoolQC"].fillna("None")
        data["MiscFeature"] = data["MiscFeature"].fillna("None")
        data["Alley"] = data["Alley"].fillna("None")
        data["Fence"] = data["Fence"].fillna("None")
        data["FireplaceQu"] = data["FireplaceQu"].fillna("None")
        data["LotFrontage"] = data.groupby("Neighborhood")["LotFrontage"].transform(
            lambda x: x.fillna(x.median()))
        for col in ('GarageType', 'GarageFinish', 'GarageQual', 'GarageCond'):
            data[col] = data[col].fillna('None')
        for col in ('GarageYrBlt', 'GarageArea', 'GarageCars'):
            data[col] = data[col].fillna(0)
        for col in ('BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF',
                    'TotalBsmtSF', 'BsmtFullBath', 'BsmtHalfBath'):
            data[col] = data[col].fillna(0)
        for col in ('BsmtQual', 'BsmtCond', 'BsmtExposure',
                    'BsmtFinType1', 'BsmtFinType2'):
            data[col] = data[col].fillna('None')
        data["MasVnrType"] = data["MasVnrType"].fillna("None")
        data["MasVnrArea"] = data["MasVnrArea"].fillna(0)
        data['MSZoning'] = data['MSZoning'].fillna(data['MSZoning'].mode()[0])
        data = data.drop(['Utilities'], axis=1)
        data["Functional"] = data["Functional"].fillna("Typ")
        data['Electrical'] = data['Electrical'].fillna(data['Electrical'].mode()[0])
        data['KitchenQual'] = data['KitchenQual'].fillna(data['KitchenQual'].mode()[0])
        data['Exterior1st'] = data['Exterior1st'].fillna(data['Exterior1st'].mode()[0])
        data['Exterior2nd'] = data['Exterior2nd'].fillna(data['Exterior2nd'].mode()[0])
        data['SaleType'] = data['SaleType'].fillna(data['SaleType'].mode()[0])
        data['MSSubClass'] = data['MSSubClass'].fillna("None")
        logger.info(f"Missing data handled. Current columns: {data.columns.tolist()}")
        return data

    def _transform_features(self, data):
        data['MSSubClass'] = data['MSSubClass'].apply(str)
        data['OverallCond'] = data['OverallCond'].astype(str)
        data['YrSold'] = data['YrSold'].astype(str)
        data['MoSold'] = data['MoSold'].astype(str)
        logger.info(f"Feature transformation complete. Current columns: {data.columns.tolist()}")
        return data

    def _label_encoding(self, data):
        for c in self.cols_to_encode:
            if c in data.columns and c in self.label_encoders:
                encoder = self.label_encoders[c]
                data[c] = data[c].map(lambda s: encoder.transform([s])[0] if s in encoder.classes_ else -1)
                logger.info(f"Column {c} label encoded. Unique values: {data[c].unique()}")
        return data

    def _handle_skewed_features(self, data):
        numeric_feats = data.dtypes[data.dtypes != "object"].index
        skewed_feats = data[numeric_feats].apply(lambda x: skew(x.dropna())).sort_values(ascending=False)
        skewness = skewed_feats[abs(skewed_feats) > 0.75]
        skewed_features = skewness.index
        lam = 0.15
        for feat in skewed_features:
            data[feat] = boxcox1p(data[feat], lam)
            logger.info(f"Skewness handled for feature: {feat}")
        return data

    def load_label_encoders(self, filepath):
        """
        Load label encoders from a file.
        """
        with open(filepath, 'rb') as f:
            self.label_encoders = pickle.load(f)
        print(f"Label encoders loaded from {filepath}")