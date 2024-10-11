import pandas as pd
import numpy as np
from scipy.special import boxcox1p
from scipy.stats import skew
from sklearn.preprocessing import LabelEncoder
import pickle

class FeatureEngineer:
    def __init__(self):
        self.ntrain = 0
        self.ntest = 0
        self.y_train = None
        self.label_encoders = {}

    def engineer_features(self, train, test):
        # Combine train and test data
        self.ntrain = train.shape[0]
        self.ntest = test.shape[0]
        self.y_train = train['SalePrice'].values

        all_data = pd.concat((train, test)).reset_index(drop=True)
        all_data.drop(['SalePrice'], axis=1, inplace=True)

        # Handle missing data
        all_data = self._handle_missing_data(all_data)

        # Transform numerical features to categorical
        all_data = self._transform_features(all_data)

        # Label Encoding
        all_data = self._label_encoding(all_data)

        # Add new features
        all_data['TotalSF'] = all_data['TotalBsmtSF'] + all_data['1stFlrSF'] + all_data['2ndFlrSF']

        # Handle skewed features
        all_data = self._handle_skewed_features(all_data)

        # One-Hot Encoding
        all_data = pd.get_dummies(all_data)

        # Align train and test data
        train = all_data[:self.ntrain]
        test = all_data[self.ntrain:]

        return train, test, self.y_train, self.label_encoders

    def _handle_missing_data(self, all_data):
        # Fill missing values as per original logic
        all_data["PoolQC"] = all_data["PoolQC"].fillna("None")
        all_data["MiscFeature"] = all_data["MiscFeature"].fillna("None")
        all_data["Alley"] = all_data["Alley"].fillna("None")
        all_data["Fence"] = all_data["Fence"].fillna("None")
        all_data["FireplaceQu"] = all_data["FireplaceQu"].fillna("None")
        all_data["LotFrontage"] = all_data.groupby("Neighborhood")["LotFrontage"].transform(
            lambda x: x.fillna(x.median()))
        for col in ('GarageType', 'GarageFinish', 'GarageQual', 'GarageCond'):
            all_data[col] = all_data[col].fillna('None')
        for col in ('GarageYrBlt', 'GarageArea', 'GarageCars'):
            all_data[col] = all_data[col].fillna(0)
        for col in ('BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF',
                    'TotalBsmtSF', 'BsmtFullBath', 'BsmtHalfBath'):
            all_data[col] = all_data[col].fillna(0)
        for col in ('BsmtQual', 'BsmtCond', 'BsmtExposure',
                    'BsmtFinType1', 'BsmtFinType2'):
            all_data[col] = all_data[col].fillna('None')
        all_data["MasVnrType"] = all_data["MasVnrType"].fillna("None")
        all_data["MasVnrArea"] = all_data["MasVnrArea"].fillna(0)
        all_data['MSZoning'] = all_data['MSZoning'].fillna(all_data['MSZoning'].mode()[0])
        all_data = all_data.drop(['Utilities'], axis=1)
        all_data["Functional"] = all_data["Functional"].fillna("Typ")
        all_data['Electrical'] = all_data['Electrical'].fillna(all_data['Electrical'].mode()[0])
        all_data['KitchenQual'] = all_data['KitchenQual'].fillna(all_data['KitchenQual'].mode()[0])
        all_data['Exterior1st'] = all_data['Exterior1st'].fillna(all_data['Exterior1st'].mode()[0])
        all_data['Exterior2nd'] = all_data['Exterior2nd'].fillna(all_data['Exterior2nd'].mode()[0])
        all_data['SaleType'] = all_data['SaleType'].fillna(all_data['SaleType'].mode()[0])
        all_data['MSSubClass'] = all_data['MSSubClass'].fillna("None")

        # Check remaining missing values if any
        all_data_na = (all_data.isnull().sum() / len(all_data)) * 100
        all_data_na = all_data_na.drop(all_data_na[all_data_na == 0].index).sort_values(ascending=False)
        if all_data_na.shape[0] > 0:
            print("There are still missing values in the data:")
            print(all_data_na)
        else:
            print("No missing values remaining.")
        return all_data

    def _transform_features(self, all_data):
        # MSSubClass=The building class
        all_data['MSSubClass'] = all_data['MSSubClass'].apply(str)

        # Changing OverallCond into a categorical variable
        all_data['OverallCond'] = all_data['OverallCond'].astype(str)

        # Year and month sold are transformed into categorical features.
        all_data['YrSold'] = all_data['YrSold'].astype(str)
        all_data['MoSold'] = all_data['MoSold'].astype(str)
        return all_data

    def _label_encoding(self, all_data):
        cols = ('FireplaceQu', 'BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond',
                'ExterQual', 'ExterCond', 'HeatingQC', 'PoolQC', 'KitchenQual',
                'BsmtFinType1', 'BsmtFinType2', 'Functional', 'Fence', 'BsmtExposure',
                'GarageFinish', 'LandSlope', 'LotShape', 'PavedDrive', 'Street',
                'Alley', 'CentralAir', 'MSSubClass', 'OverallCond', 'YrSold', 'MoSold')

        for c in cols:
            lbl = LabelEncoder()
            lbl.fit(list(all_data[c].values))
            all_data[c] = lbl.transform(list(all_data[c].values))
            self.label_encoders[c] = lbl
        return all_data

    def save_label_encoders(self, filepath):
        """
        Save the label encoders to a file.
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self.label_encoders, f)
        print(f"Label encoders saved to {filepath}")

    def load_label_encoders(self, filepath):
        """
        Load label encoders from a file.
        """
        with open(filepath, 'rb') as f:
            self.label_encoders = pickle.load(f)
        print(f"Label encoders loaded from {filepath}")

    def _handle_skewed_features(self, all_data):
        numeric_feats = all_data.dtypes[all_data.dtypes != "object"].index

        skewed_feats = all_data[numeric_feats].apply(lambda x: skew(x.dropna())).sort_values(ascending=False)
        skewness = pd.DataFrame({'Skew': skewed_feats})
        skewness = skewness[abs(skewness) > 0.75]

        skewed_features = skewness.index
        lam = 0.15
        for feat in skewed_features:
            all_data[feat] = boxcox1p(all_data[feat], lam)
        return all_data

