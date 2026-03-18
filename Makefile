include .env
export

SHELL=/bin/bash
PATH := .venv/bin:$(PATH)
export TEST?=./tests
IMAGE_NAME=taskshare-service


install-local:
	uv sync --all-groups

lint: 
	@uv run ruff check .
	@uv run ruff format --check .

lint-fix:
	@uv run ruff check . --fix
	@uv run ruff format .


run-local:
	@docker compose -f docker-compose-local.yml up -d db_local;
	@uv run python manage.py runserver

makemigrations:
	@uv run python manage.py makemigrations

migrate:
	@uv run python manage.py migrate

apply-migrations:
	@make makemigrations
	@make migrate

createsuperuser:
	@uv run python manage.py createsuperuser

.PHONY: run-local install-local lint lint-fix makemigrations migrate createsuperuser