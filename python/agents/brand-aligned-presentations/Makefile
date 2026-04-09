.PHONY: install backend test

install:
	uv sync

backend:
	uv run python deployment/deploy.py --mode create

update:
	uv run python deployment/deploy.py --mode update

test:
	rm -rf .pytest_cache __pycache__ tests/__pycache__
	uv run pytest --cache-clear
