.PHONY: test test-verbose test-coverage clean install help

# Default target
help:
	@echo "Available commands:"
	@echo "  install       - Install dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-verbose  - Run tests with detailed output"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  test-auth     - Run authentication tests only"
	@echo "  test-models   - Run model tests only"
	@echo "  test-posts    - Run post tests only"
	@echo "  test-users    - Run user tests only"
	@echo "  clean         - Clean up test artifacts"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with detailed output
test-verbose:
	python -m pytest tests/ -v -s

# Run tests with coverage report
test-coverage:
	python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# Run specific test files
test-auth:
	python -m pytest tests/test_auth.py -v

test-models:
	python -m pytest tests/test_models.py -v

test-posts:
	python -m pytest tests/test_posts.py -v

test-users:
	python -m pytest tests/test_users.py -v

test-main:
	python -m pytest tests/test_main.py -v

# Run tests and stop on first failure
test-fail-fast:
	python -m pytest tests/ -v -x

# Run only failed tests from last run
test-failed:
	python -m pytest tests/ -v --lf

# Run tests matching a pattern
test-pattern:
	python -m pytest tests/ -v -k "$(PATTERN)"

# Clean up
clean:
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.db" -delete
