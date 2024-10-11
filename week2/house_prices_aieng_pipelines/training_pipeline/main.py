import sys
import os
import pandas as pd
import numpy as np
import configparser
import datetime

# Add the path to access the catalog and model classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training_pipeline.data_consumer.data_loader import DataLoader
from training_pipeline.data_preprocessing.data_preprocessing import DataPreprocessor
from training_pipeline.feature_engineering.feature_engineering import FeatureEngineer
from training_pipeline.model_training.model_training import BaseModel
from training_pipeline.model_training.model_stacking import StackingAveragedModels
from capabilities.model_catalog import ModelCatalog

from sklearn.linear_model import Lasso, ElasticNet
from sklearn.kernel_ridge import KernelRidge
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import mean_squared_error

def rmsle(y, y_pred):
    """Calculate Root Mean Squared Logarithmic Error."""
    return np.sqrt(mean_squared_error(y, y_pred))

def main():
    # Load the INI configuration file
    config = configparser.ConfigParser()
    config.read('../config/training_pipeline_config.ini')

    # Load paths from the configuration
    train_data_path = config['paths']['train_data']
    test_data_path = config['paths']['test_data']
    label_encoders_path = config['paths']['label_encoders']
    model_catalog_path = config['paths']['model_catalog_path']
    final_model_path = config['paths']['final_model']

    # Load training parameters
    lasso_alpha = float(config['training_params']['lasso_alpha'])
    enet_alpha = float(config['training_params']['enet_alpha'])
    enet_l1_ratio = float(config['training_params']['enet_l1_ratio'])
    gboost_estimators = int(config['training_params']['gboost_estimators'])
    gboost_learning_rate = float(config['training_params']['gboost_learning_rate'])
    gboost_max_depth = int(config['training_params']['gboost_max_depth'])

    # Load ensemble weights
    ensemble_weight_stacked = float(config['stacking']['ensemble_weight_stacked'])
    ensemble_weight_xgb = float(config['stacking']['ensemble_weight_xgb'])
    ensemble_weight_lgb = float(config['stacking']['ensemble_weight_lgb'])

    # Step 1: Load data
    data_loader = DataLoader(train_path=train_data_path, test_path=test_data_path)
    train, test = data_loader.load_data()

    # Step 2: Preprocess data
    preprocessor = DataPreprocessor()
    train, test = preprocessor.preprocess(train, test)

    # Step 3: Feature Engineering
    engineer = FeatureEngineer()
    train_data, test_data, y_train, label_encoders = engineer.engineer_features(train, test)

    # Save the label encoders
    engineer.save_label_encoders(label_encoders_path)

    # Step 4: Define models
    lasso = make_pipeline(RobustScaler(), Lasso(alpha=lasso_alpha, random_state=1))
    ENet = make_pipeline(RobustScaler(), ElasticNet(alpha=enet_alpha, l1_ratio=enet_l1_ratio, random_state=3))
    KRR = KernelRidge(alpha=0.6, kernel='polynomial', degree=2, coef0=2.5)
    GBoost = GradientBoostingRegressor(
        n_estimators=gboost_estimators, learning_rate=gboost_learning_rate,
        max_depth=gboost_max_depth, max_features='sqrt',
        min_samples_leaf=15, min_samples_split=10,
        loss='huber', random_state=5
    )
    model_xgb = xgb.XGBRegressor(
        colsample_bytree=0.4603, gamma=0.0468,
        learning_rate=0.05, max_depth=3,
        min_child_weight=1.7817, n_estimators=2200,
        reg_alpha=0.4640, reg_lambda=0.8571,
        subsample=0.5213, random_state=7, nthread=-1
    )
    model_lgb = lgb.LGBMRegressor(
        objective='regression', num_leaves=5,
        learning_rate=0.05, n_estimators=720,
        max_bin=55, bagging_fraction=0.8,
        bagging_freq=5, feature_fraction=0.2319,
        feature_fraction_seed=9, bagging_seed=9,
        min_data_in_leaf=6, min_sum_hessian_in_leaf=11
    )

    # Step 5: Evaluate base models
    models = [
        BaseModel(lasso, 'Lasso'),
        BaseModel(ENet, 'ElasticNet'),
        BaseModel(KRR, 'Kernel Ridge'),
        BaseModel(GBoost, 'Gradient Boosting'),
        BaseModel(model_xgb, 'XGBoost'),
        BaseModel(model_lgb, 'LightGBM')
    ]

    for model in models:
        score = model.rmsle_cv(train_data.values, y_train)
        print(f"{model.name} score: {score.mean():.4f} ({score.std():.4f})")

    # Step 6: Stacking models
    stacked_averaged_models = StackingAveragedModels(
        base_models=(ENet, GBoost, KRR),
        meta_model=lasso
    )
    stacked_averaged_models.fit(train_data.values, y_train)
    stacked_train_pred = stacked_averaged_models.predict(train_data.values)
    stacked_pred = np.expm1(stacked_averaged_models.predict(test_data.values))

    # Step 7: Evaluate stacking model
    stack_rmse = rmsle(y_train, stacked_train_pred)
    print('Stacked model RMSE:', stack_rmse)

    # Step 8: Fit other models and predict
    model_xgb.fit(train_data, y_train)
    xgb_train_pred = model_xgb.predict(train_data)
    xgb_pred = np.expm1(model_xgb.predict(test_data.values))
    xgb_rmse = rmsle(y_train, xgb_train_pred)
    print('XGBoost RMSE:', xgb_rmse)

    model_lgb.fit(train_data, y_train)
    lgb_train_pred = model_lgb.predict(train_data)
    lgb_pred = np.expm1(model_lgb.predict(test_data.values))
    lgb_rmse = rmsle(y_train, lgb_train_pred)
    print('LightGBM RMSE:', lgb_rmse)

    # Step 9: Ensemble prediction
    ensemble = stacked_pred * ensemble_weight_stacked + xgb_pred * ensemble_weight_xgb + lgb_pred * ensemble_weight_lgb

    # Step 10: Save the best performing model using ModelCatalog
    model_catalog = ModelCatalog(catalog_path = model_catalog_path)

    project_name = 'House Price Prediction'
    project_uuid = model_catalog.create_or_retrieve_project(project_name)

    model_card = {
        'project_name': project_name,
        'algorithm': 'Stacked Averaged Models',
        'rmse': stack_rmse,
        'date_of_training': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'hyperparameters': {
            'alpha': lasso_alpha,
            'max_depth': gboost_max_depth
        },
        'features': list(train_data.columns),
        'stage': 'dev'
    }

    model_catalog.save_model(project_uuid, stacked_averaged_models, model_card=model_card, model_columns=train_data.columns)

    # Save the final model
    # final_model_file = os.path.join(model_output_dir, 'final_model.pkl')
    # stacked_averaged_models.save(final_model_file)
    # print(f"Final model saved at {final_model_file}")


if __name__ == "__main__":
    main()
