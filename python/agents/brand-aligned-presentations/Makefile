.PHONY: install backend update test

install:
	uv sync

backend:
	@if [ -f deployment/deploy.py ]; then \
		uv run python deployment/deploy.py --mode create; \
	elif [ -f presentation_agent/app_utils/deploy.py ]; then \
		uv run python presentation_agent/app_utils/deploy.py --mode create; \
	else \
		echo "Error: deploy.py not found in deployment/ or presentation_agent/app_utils/"; \
		exit 1; \
	fi

update:
	@if [ -f deployment/deploy.py ]; then \
		uv run python deployment/deploy.py --mode update; \
	elif [ -f presentation_agent/app_utils/deploy.py ]; then \
		uv run python presentation_agent/app_utils/deploy.py --mode update; \
	else \
		echo "Error: deploy.py not found in deployment/ or presentation_agent/app_utils/"; \
		exit 1; \
	fi

test:
	rm -rf .pytest_cache __pycache__ tests/__pycache__
	uv run pytest --cache-clear
