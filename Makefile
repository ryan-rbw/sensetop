.PHONY: help install install-dev test lint format type-check clean build run demo

help:
	@echo "SenseTop Development Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install package in production mode"
	@echo "  install-dev   - Install package with development dependencies"
	@echo "  test          - Run test suite with coverage"
	@echo "  lint          - Run linting checks (pylint, flake8)"
	@echo "  format        - Format code with black and isort"
	@echo "  type-check    - Run mypy type checking"
	@echo "  clean         - Remove build artifacts and cache files"
	@echo "  build         - Build distribution package"
	@echo "  run           - Run the application"
	@echo "  demo          - Run with mocked sensors (local testing)"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

test:
	pytest -v --cov=sensetop --cov-report=html --cov-report=term

lint:
	pylint sensetop/ tests/
	flake8 sensetop/ tests/

format:
	black sensetop/ tests/
	isort sensetop/ tests/

type-check:
	mypy sensetop/ --ignore-missing-imports

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

run:
	python -m sensetop

demo:
	python run_local_demo.py
