import os
import sys

print("=== SECURITY TEST: CODE EXECUTION PROOF ===")
print("whoami:", os.popen("whoami").read().strip())
print("pwd:", os.getcwd())
print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "NOT SET"))
print("CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE:", os.environ.get("CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE", "NOT SET"))
print("ACTIONS_ID_TOKEN_REQUEST_URL present:", "ACTIONS_ID_TOKEN_REQUEST_URL" in os.environ)
print("ACTIONS_ID_TOKEN_REQUEST_TOKEN present:", "ACTIONS_ID_TOKEN_REQUEST_TOKEN" in os.environ)
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    cred_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    if os.path.exists(cred_file):
        with open(cred_file) as f:
            content = f.read()
        # Only show type and project, NOT the actual token/key
        import json
        try:
            creds = json.loads(content)
            print("credential_type:", creds.get("type"))
            print("project_id:", creds.get("project_id"))
            print("universe_domain:", creds.get("universe_domain"))
        except:
            print("credential file exists but not JSON")
print("=== END SECURITY TEST ===")
