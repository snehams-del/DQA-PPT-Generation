# --- BQ Observability Agent Hooks ---
# These targets inject interactive dataset setup into the Agent Starter Pack lifecycle

.PHONY: setup_dataset grant_permissions


# We declare `grant_permissions` to entirely override or pre-empt the standard deployment 
# so we can securely inject the env var.
backend: setup_dataset grant_permissions

setup_dataset:
	@echo "==============================================================================="
	@echo "| BigQuery Dataset Setup                                                      |"
	@echo "==============================================================================="
	@touch .env
	@if ! grep -q "^GOOGLE_CLOUD_PROJECT=" .env; then \
		PROJECT_ID=$$(gcloud config get-value project); \
		echo "GOOGLE_CLOUD_PROJECT=$$PROJECT_ID" >> .env; \
	fi
	@if ! grep -q "^GOOGLE_CLOUD_LOCATION=" .env; then \
		echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env; \
	fi
	@read -p "Do you want to prepare the BigQuery dataset for this agent? (y/n) " prepare_dataset; \
	if [ "$$prepare_dataset" = "y" ] || [ "$$prepare_dataset" = "Y" ]; then \
		echo "Preparing BQ dataset..."; \
		read -p "Enter BigQuery Dataset ID [default: adk_agent_analytics]: " dataset_id; \
		dataset_id=$${dataset_id:-adk_agent_analytics}; \
		if ! grep -q "^BQ_ANALYTICS_DATASET_ID=" .env; then \
			echo "BQ_ANALYTICS_DATASET_ID=$$dataset_id" >> .env; \
		else \
			if [ "$$(uname)" = "Darwin" ]; then \
				sed -i '' "s/^BQ_ANALYTICS_DATASET_ID=.*/BQ_ANALYTICS_DATASET_ID=$$dataset_id/" .env; \
			else \
				sed -i "s/^BQ_ANALYTICS_DATASET_ID=.*/BQ_ANALYTICS_DATASET_ID=$$dataset_id/" .env; \
			fi \
		fi; \
		export BQ_ANALYTICS_DATASET_ID=$$dataset_id; \
		if [ -f "agent_observability_bq/shared_libraries/prepare_dataset.py" ]; then \
			uv run python agent_observability_bq/shared_libraries/prepare_dataset.py; \
		else \
			echo "Warning: prepare_dataset.py not found in scaffolded project."; \
		fi \
	else \
		echo "Skipping BQ dataset preparation."; \
	fi

grant_permissions:
	@echo "==============================================================================="
	@echo "| Deploying Agent Engine with BQ Observability & Granting Permissions         |"
	@echo "==============================================================================="
	@if grep -q "^BQ_ANALYTICS_DATASET_ID=" .env; then \
		DATASET_VAL=$$(grep "^BQ_ANALYTICS_DATASET_ID=" .env | cut -d '=' -f2- | tr -d "'\""); \
	else \
		DATASET_VAL="adk_agent_analytics"; \
	fi; \
	if grep -q "^GOOGLE_CLOUD_PROJECT=" .env; then \
		PROJECT_VAL=$$(grep "^GOOGLE_CLOUD_PROJECT=" .env | cut -d '=' -f2- | tr -d "'\""); \
	else \
		PROJECT_VAL=$$(gcloud config get-value project); \
	fi; \
	if grep -q "^GOOGLE_CLOUD_LOCATION=" .env; then \
		LOCATION_VAL=$$(grep "^GOOGLE_CLOUD_LOCATION=" .env | cut -d '=' -f2- | tr -d "'\""); \
	else \
		LOCATION_VAL="us-central1"; \
	fi; \
	echo "Injecting BQ_ANALYTICS_DATASET_ID=$$DATASET_VAL and GOOGLE_CLOUD_LOCATION=$$LOCATION_VAL via --set-env-vars..."; \
	(uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate > agent_observability_bq/app_utils/.requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project > agent_observability_bq/app_utils/.requirements.txt) && \
	uv run -m agent_observability_bq.app_utils.deploy \
		--source-packages=./agent_observability_bq \
		--entrypoint-module=agent_observability_bq.agent_engine_app \
		--entrypoint-object=agent_engine \
		--requirements-file=agent_observability_bq/app_utils/.requirements.txt \
		--set-env-vars="BQ_ANALYTICS_DATASET_ID=$$DATASET_VAL,GOOGLE_CLOUD_LOCATION=$$LOCATION_VAL" \
		$(if $(AGENT_IDENTITY),--agent-identity) \
		$(if $(filter command line,$(origin SECRETS)),--set-secrets="$(SECRETS)"); \
	if [ -f "agent_observability_bq/shared_libraries/grant_permissions.sh" ]; then \
		bash agent_observability_bq/shared_libraries/grant_permissions.sh; \
	else \
		echo "Warning: agent_observability_bq/shared_libraries/grant_permissions.sh not found."; \
	fi
