# Makefile for the debug_python_the_right_way project

IMAGE_NAME = gnmi-interfaces
IMAGE_TAG = latest

.PHONY: install
install:
	uv sync

.PHONY: run
run:
	uv run --env-file .env answer/get_interfaces.py

.PHONY: lint
lint:
	uv run ruff check .

.PHONY: test
test:
	uv run pytest -v

.PHONY: check
check: lint test

.PHONY: build
build:
	podman build --platform=linux/amd64 -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: up
up:
	podman run --rm --env-file .env $(IMAGE_NAME):$(IMAGE_TAG)
