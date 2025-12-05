PYTHON=python3.12
PIP=pip
VENV=.venv

.PHONY: help install run build up down lint format test

help:
	@echo "Makefile commands:"
	@echo "  make install   - create venv and install dependencies"
	@echo "  make run       - run uvicorn (local, reload)"
	@echo "  make build     - build Docker image"
	@echo "  make up        - docker-compose up --build"
	@echo "  make down      - docker-compose down"
	@echo "  make lint      - run pep8 (pycodestyle)"
	@echo "  make format    - run black and isort"
	@echo "  make test      - run pytest"
	@echo "  make coverage  - run pytest with coverage"
	@echo "  make venv      - create virtualenv and install dependencies"
	@echo "
	# To create and activate venv manually (Linux/macOS):"
	@echo "  python3 -m venv .venv"
	@echo "  source .venv/bin/activate"
	@echo "# On Windows (PowerShell):"
	@echo "  python -m venv .venv"
	@echo "  .\\.venv\\Scripts\\Activate.ps1"

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	source .venv/bin/activate

run:
	$(VENV)/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker build -t document-service:latest .

up:
	docker compose up --build

down:
	docker compose down

lint:
	# pep8 (pycodestyle) checks
	$(VENV)/bin/pycodestyle app tests --ignore=E501,W503,W293 || true

format:
	$(VENV)/bin/isort .
	$(VENV)/bin/black .

test:
	$(VENV)/bin/pytest -q

coverage:
	$(VENV)/bin/pytest --cov=app --cov-report=html --cov-report=term-missing
