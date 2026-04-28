# Makefile for the debug_python_the_right_way project

IMAGE_NAME = gnmi-interfaces
IMAGE_TAG = latest

.PHONY: install run lint test check build up

install:
	uv sync

run:
	uv run --env-file .env answer/get_interfaces.py

lint:
	uv run ruff check .

test:
	uv run pytest -v

check: lint test

build:
	podman build --platform=linux/amd64 -t $(IMAGE_NAME):$(IMAGE_TAG) .

up:
	podman run --rm --env-file .env $(IMAGE_NAME):$(IMAGE_TAG)
