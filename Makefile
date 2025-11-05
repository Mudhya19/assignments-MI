.PHONY: install run test format lint clean

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run the application
run:
	python src/main.py

# Run tests
test:
	pytest tests/

# Format code with black
format:
	black src/ tests/

# Lint code with flake8
lint:
	flake8 src/ tests/

# Clean up
clean:
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf .pytest_cache/
	rm -rf .coverage
