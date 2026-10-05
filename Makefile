.PHONY: help install lint test build up down logs clean

help:
	@echo "install | lint | test | build | up | down | logs | clean"

install:
	python -m venv .venv
	. .venv/Scripts/activate && pip install -U pip && pip install -r requirements.txt

lint:
	ruff check .

test:
	pytest -v

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true