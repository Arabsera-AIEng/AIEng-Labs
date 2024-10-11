from sklearn.model_selection import KFold, cross_val_score
import numpy as np

class BaseModel:
    def __init__(self, model, name, n_folds=5):
        self.model = model
        self.name = name
        self.n_folds = n_folds
        self.score = None

    def rmsle_cv(self, X, y):
        kf = KFold(self.n_folds, shuffle=True, random_state=42)
        rmse = np.sqrt(-cross_val_score(self.model, X, y, scoring="neg_mean_squared_error", cv=kf))
        self.score = rmse.mean()
        return rmse

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

