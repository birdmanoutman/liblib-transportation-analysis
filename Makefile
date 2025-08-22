.PHONY: install install-dev test test-unit test-integration coverage lint format type-check pre-commit-install clean

install:
	python -m pip install -r requirements.txt

install-dev:
	python -m pip install -r requirements.txt -r requirements-dev.txt -r requirements-test.txt

test:
	pytest

test-unit:
	pytest -m unit -v --tb=short

test-integration:
	pytest -m integration -v --tb=short

coverage:
	pytest -v --tb=short --cov=scripts --cov-report=term-missing --cov-report=html:htmlcov

lint:
	ruff check .
	black --check .
	isort --check-only .

format:
	ruff check --fix .
	black .
	isort .

type-check:
	mypy scripts tests

pre-commit-install:
	pre-commit install

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage* build dist


