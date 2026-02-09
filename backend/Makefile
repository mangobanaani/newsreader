.PHONY: lint format check test type-check all

# Run all checks (same as CI)
all: check test

# Lint and format check (no changes)
check: format-check lint type-check

# Auto-fix lint issues and format code
fix:
	ruff check --fix app tests
	ruff format app tests

# Check formatting without changes
format-check:
	ruff format --check app tests

# Format code
format:
	ruff format app tests

# Run linter
lint:
	ruff check app tests

# Run type checker
type-check:
	mypy app

# Run tests
test:
	pytest -v --cov=app

# Run tests with coverage report
test-cov:
	pytest -v --cov=app --cov-report=html --cov-report=term
