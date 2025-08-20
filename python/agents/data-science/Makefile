install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev

playground:
	uv run adk web --port 8501

lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

test:
	uv run pytest tests/integration

eval:
	uv run pytest eval

deploy-infra:
	@PROJECT_ID=$$(gcloud config get-value project) && \
	AGENT_NAME=$${AGENT_NAME:-data-science} && \
	BUCKET_NAME="$$PROJECT_ID-terraform-state" && \
	STATE_PREFIX="agents/$$AGENT_NAME" && \
	echo "Checking if bucket $$BUCKET_NAME exists..." && \
	if ! gcloud storage ls -b gs://$$BUCKET_NAME >/dev/null 2>&1; then \
		echo "Creating bucket $$BUCKET_NAME..."; \
		gcloud storage buckets create gs://$$BUCKET_NAME; \
	else \
		echo "Bucket $$BUCKET_NAME already exists."; \
	fi && \
	echo "Project ID: $$PROJECT_ID" && \
	echo "State prefix: $$STATE_PREFIX" && \
	terraform -chdir=infra init -backend-config="bucket=$$BUCKET_NAME" -backend-config="prefix=$$STATE_PREFIX" && \
	terraform -chdir=infra apply -var="project_id=$$PROJECT_ID" $(if $(AGENT_NAME),-var="agent_name=$(AGENT_NAME)") -auto-approve
