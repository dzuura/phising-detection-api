.PHONY: dev prod install test clean docker-up docker-down docker-logs help

# Default target
help:
	@echo "Available commands:"
	@echo "  make dev          - Run development server with auto-reload"
	@echo "  make prod         - Run production server"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean cache files"
	@echo "  make docker-up    - Start with Docker Compose"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker logs"

# Development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Install dependencies
install:
	pip install -r requirements.txt

# Install dev dependencies
install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=app --cov-report=html

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build
