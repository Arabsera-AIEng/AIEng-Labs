.PHONY: run run-container

APP_NAME ?= house-price-predictor

run:
	@streamlit run app.py --server.port=8080 --server.address=0.0.0.0

run-container:
	@docker build . -t ${APP_NAME}
	@docker run -p 8080:8080 ${APP_NAME}
