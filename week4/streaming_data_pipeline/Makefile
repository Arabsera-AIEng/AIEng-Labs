# Variables
COMPOSE_FILE=docker-compose.yml
DOCKER_COMPOSE=docker-compose -f $(COMPOSE_FILE)
AIRFLOW_CMD=$(DOCKER_COMPOSE) run --rm airflow-webserver

# Targets
.PHONY: help build start init create-user stop clean logs setup reset psql

help: ## Display available commands
	@echo "Streaming Data Pipeline Makefile"
	@echo
	@echo "Available commands:"
	@echo "  make build         Build Docker images for the pipeline"
	@echo "  make start         Start all services"
	@echo "  make init          Initialize the Airflow database"
	@echo "  make create-user   Create an Airflow admin user"
	@echo "  make stop          Stop all services"
	@echo "  make clean         Remove data volumes"
	@echo "  make logs          Tail logs for all services"
	@echo "  make setup         Run full setup from build to user creation"
	@echo "  make reset         Stop services and clean up volumes"
	@echo "  make psql          Connect to PostgreSQL and run SQL commands"

build: ## Build Docker images for the pipeline
	docker build -t data_producer_image ./data_producer
	docker build -t data_processor_image ./data_processor

start: ## Start all services
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

stop: ## Stop all services
	$(DOCKER_COMPOSE) down

clean: stop ## Stop services and remove data volumes
	docker volume rm streaming_data_pipeline_postgres_data

logs: ## Tail logs for all services
	$(DOCKER_COMPOSE) logs -f

setup: build start init create-user start ## Full setup from building images to creating user

reset: stop clean ## Stop services and clean up volumes

psql:
	$(DOCKER_COMPOSE) exec postgres psql -U airflow -d streaming_db
