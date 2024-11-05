# Variables
COMPOSE_FILE=docker-compose.yaml
DOCKER_COMPOSE=docker-compose -f $(COMPOSE_FILE)
AIRFLOW_CMD=$(DOCKER_COMPOSE) run --rm webserver

# Targets
.PHONY: help build start init create-user stop clean logs setup reset

help: ## Display available commands
	@echo "Airflow Pipeline Management Makefile"
	@echo
	@echo "Available commands:"
	@echo "  make build         Build Docker images for the pipeline steps"
	@echo "  make start         Start the Airflow pipeline services"
	@echo "  make init          Initialize the Airflow database"
	@echo "  make create-user   Create an Airflow admin user"
	@echo "  make stop          Stop the Airflow pipeline services"
	@echo "  make clean         Remove all data volumes"
	@echo "  make logs          Tail the logs of all running services"
	@echo "  make setup         Run full setup from build to user creation"
	@echo "  make reset         Stop services and clean up all volumes"

build: ## Build Docker images for all pipeline steps
	docker build -t download_data_image ./steps/download_data
	docker build -t process_data_image ./steps/process_data
	docker build -t validate_data_image ./steps/validate_data
	docker build -t load_data_image ./steps/load_data

start: ## Start Airflow and PostgreSQL services
	$(DOCKER_COMPOSE) up -d

init: ## Initialize the Airflow database
	$(AIRFLOW_CMD) airflow db init

create-user: ## Create an Airflow admin user
	$(AIRFLOW_CMD) airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com

stop: ## Stop all running Airflow services
	$(DOCKER_COMPOSE) down

clean: stop ## Stop services and remove data volumes
	docker volume rm nyc_taxi_data_etl_pipeline_postgres_data

logs: ## Tail logs for all services
	$(DOCKER_COMPOSE) logs -f

setup: start init create-user start ## Full setup from building images to creating user

reset: stop clean ## Stop services and clean up all volumes