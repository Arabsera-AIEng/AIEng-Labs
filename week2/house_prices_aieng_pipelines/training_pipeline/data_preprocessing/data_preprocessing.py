import pandas as pd
import numpy as np

class DataPreprocessor:
    def __init__(self):
        self.train_ID = None
        self.test_ID = None

    def preprocess(self, train, test):
        # Save 'Id' columns
        self.train_ID = train['Id']
        self.test_ID = test['Id']

        # Drop 'Id' columns
        train.drop('Id', axis=1, inplace=True)
        test.drop('Id', axis=1, inplace=True)

        # Remove outliers
        train = self._remove_outliers(train)

        # Log-transform the target variable
        train["SalePrice"] = np.log1p(train["SalePrice"])

        return train, test

    def _remove_outliers(self, data):
        data = data.drop(data[(data['GrLivArea'] > 4000) & (data['SalePrice'] < 300000)].index)
        return data

