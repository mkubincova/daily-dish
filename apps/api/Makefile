.PHONY: dev db-up db-down db-migrate db-reset test lint

dev:
	uv run uvicorn app.main:app --reload --port 8000

db-up:
	docker compose -f ../../docker-compose.yml up -d

db-down:
	docker compose -f ../../docker-compose.yml down

db-migrate:
	env $(shell cat .env | grep -v '^#' | xargs) uv run alembic upgrade head

db-reset:
	env $(shell cat .env | grep -v '^#' | xargs) uv run alembic downgrade base && \
	env $(shell cat .env | grep -v '^#' | xargs) uv run alembic upgrade head

test:
	uv run pytest

lint:
	uv run ruff check app/ tests/ && uv run ruff format --check app/ tests/
