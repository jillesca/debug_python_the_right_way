# Makefile for the debug_python_the_right_way project

# Variables
SCRIPT=get_interfaces.py

# Default target
.PHONY: all
all: build run

# Build step: Update the project's environment using uv sync
.PHONY: build
build:
	uv sync

# Run step: Execute the script using uv
.PHONY: run
run:
	uv run $(SCRIPT)
