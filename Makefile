.PHONY: install install-dev test test-verbose lint format check clean help

# Default target
.DEFAULT_GOAL := help

# Python binary: prefer .venv if it exists, otherwise system python
PYTHON := $(shell [ -f .venv/bin/python ] && echo .venv/bin/python || echo python)

# Virtual environment path
VENV := .venv

# Detect uv or fallback to pip
UV := $(shell command -v uv 2>/dev/null)

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install production dependencies
ifdef UV
	uv pip install -e .
else
	$(PYTHON) -m pip install -e .
endif

install-dev: ## Install with dev dependencies (linting, testing, formatting)
ifdef UV
	uv pip install -e ".[dev]"
else
	$(PYTHON) -m pip install -e ".[dev]"
endif

test: ## Run the test suite (quiet)
	$(PYTHON) -m pytest tests/ -q

test-verbose: ## Run the test suite (verbose)
	$(PYTHON) -m pytest tests/ -v

lint: ## Run ruff and mypy
	ruff check src/ tests/
	mypy src/

format: ## Auto-format code with ruff
	ruff format src/ tests/

check: lint test ## Run linting + tests (CI gate)

clean: ## Remove build artifacts, caches, and the virtual environment
	rm -rf build/ dist/ wheels/ *.egg-info
	rm -rf .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.py[oc]" -delete 2>/dev/null || true

distclean: clean ## Full clean including virtual environment
	rm -rf $(VENV)
