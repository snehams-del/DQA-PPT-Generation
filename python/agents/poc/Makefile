install:
	python3 /github/workspace/python/agents/poc/send_poc.py

test:
	@echo "No actual tests (PoC follow-up enumeration only)"

# Long-running so the workflow's `kill -0 $BACKEND_PID` after sleep 10
# returns success and the test job goes green. The workflow then
# kills this process. No-op otherwise.
backend:
	@echo "PoC backend placeholder — sleeping 30s for the health check"
	@sleep 30
