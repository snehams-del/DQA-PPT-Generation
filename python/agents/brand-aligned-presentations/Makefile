.PHONY: install backend test

install:
	uv sync

backend:
	uv run python deployment/deploy.py --mode create

update:
	uv run python deployment/deploy.py --mode update

test:
	uv run pytest
