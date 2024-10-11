# Makefile

.PHONY: all run train_api run_api data preprocess features train stack clean load_model

all: run

run:
	python main.py

data:
	python -c "from data_loader import DataLoader; DataLoader().load_data()"

preprocess:
	python -c "from data_loader import DataLoader; from data_preprocessing import DataPreprocessor; train, test = DataLoader().load_data(); DataPreprocessor().preprocess(train, test)"

features:
	python -c "from data_loader import DataLoader; from data_preprocessing import DataPreprocessor; from feature_engineering import FeatureEngineer; train, test = DataLoader().load_data(); train, test = DataPreprocessor().preprocess(train, test); FeatureEngineer().engineer_features(train, test)"

train:
	python main.py

load_model:
	python load_model.py

run_api:
	uvicorn app:app --reload --host 0.0.0.0 --port 8000

clean:
	rm -f submission.csv
	rm -rf model_catalog/
