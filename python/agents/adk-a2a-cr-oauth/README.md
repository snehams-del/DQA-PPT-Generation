# adk-a2a-cr-oauth

Google Drive reader agent deployed to Cloud Run via the A2A protocol, with OAuth handled by Gemini Enterprise.

Scaffolded with [`agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) (`--agent adk_a2a --deployment-target cloud_run`), then customized with OAuth credential injection and app-level token validation.

See the [root README](../README.md) for architectural details and key findings about how OAuth works across ADK deployment targets.

## How It Works

1. Agent is registered with Gemini Enterprise, linked to an OAuth authorization resource (`google-drive-auth`) that declares `drive.readonly` scope
2. When a user asks to read a Drive file, Gemini Enterprise triggers OAuth consent
3. Gemini Enterprise sends the user's OAuth token as `Authorization: Bearer` on every A2A POST request
4. Custom `OAuthCallContextBuilder` extracts the token from the HTTP header
5. Custom `OAuthA2aAgentExecutor` injects it into session state via `state_delta`
6. `negotiate_creds()` finds the token in `tool_context.state` and uses it to call the Drive API

## Project Structure

```
adk-a2a-cr-oauth/
├── app/
│   ├── agent.py               # Root agent with read_drive_file tool
│   ├── auths.py               # OAuth config (TOKEN_CACHE_KEY, scopes, auth scheme)
│   ├── tools.py               # negotiate_creds() + read_drive_file()
│   ├── fast_api_app.py        # A2A server with custom OAuth components
│   └── app_utils/
│       ├── telemetry.py       # Cloud Trace + logging
│       └── typing.py          # Feedback model
├── tools/
│   ├── register_oauth.py      # Register OAuth resource with Discovery Engine
│   └── test_a2a_oauth.py      # 3-layer integration test
├── Dockerfile
├── Makefile
└── pyproject.toml
```

### Key Files

**`app/fast_api_app.py`** — The main application file containing three custom components:
- `OAuthCallContextBuilder` — Extracts Bearer token from HTTP headers into A2A call context
- `OAuthA2aAgentExecutor` — Propagates call context state into ADK session via `state_delta`
- Token validation middleware — Validates token `aud`/`azp` against `OAUTH_CLIENT_ID`

**`app/tools.py`** — `negotiate_creds()` implements a three-stage credential resolution:
1. Check `tool_context.state` for cached/injected token (both direct key and `temp:` prefixed)
2. Check `tool_context.get_auth_response()` for ADK OAuth flow response (local dev)
3. Fall back to `request_credential()` if client credentials are configured (local dev), otherwise return an error

**`app/auths.py`** — OAuth configuration. `TOKEN_CACHE_KEY` is set from the `AUTH_ID` env var (default: `google-drive-auth`) and must match the authorization resource ID used during Gemini Enterprise registration.

## Requirements

- Google Cloud project with billing, **Drive API** and **Discovery Engine API** enabled
  *(Enable APIs: `gcloud services enable drive.googleapis.com discoveryengine.googleapis.com --project=YOUR_PROJECT_ID`)*
- `gcloud`, `uv`, `make`
- **Node.js and npm** (only required if you want to use the A2A Protocol Inspector UI via `make inspector`)
- OAuth 2.0 client (Web Application type) with redirect URIs:
  - `https://vertexaisearch.cloud.google.com/oauth-redirect`
  - `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html`
- Gemini Enterprise instance

## Setup & Deployment

### 1. Install dependencies

```bash
uv sync --dev
```


### 2. Local development

You have two options for local testing (they are alternatives):

**Option A: Test Agent Logic (Easiest)**
Starts the ADK Web UI where you can chat with the agent and test the OAuth flow in your browser:
```bash
make playground
```

**Option B: Test A2A Server**
Starts the FastAPI server that implements the A2A protocol (simulating Cloud Run deployment):
```bash
make local-backend
```
*Note: To test this backend, you will need to send HTTP requests to it (e.g., via `tools/test_a2a_oauth.py`) or use the A2A Protocol Inspector (requires Node.js).*

### 3. Deploy to Cloud Run

```bash
gcloud config set project <your-project-id>
make deploy
```

The service deploys with `--allow-unauthenticated` because Gemini Enterprise sends user OAuth tokens (not service identity tokens) in the `Authorization` header — Cloud Run IAM would reject these with 401. App-level token validation secures the endpoint instead.

Set the `OAUTH_CLIENT_ID` env var on Cloud Run to enable token validation:

```bash
gcloud run services update adk-a2a-cr-oauth \
  --region=us-central1 \
  --set-env-vars="OAUTH_CLIENT_ID=<your-oauth-client-id>"
```

### 4. Register OAuth authorization

```bash
make register-oauth
```

This interactively registers an OAuth authorization resource with the Discovery Engine API. You'll need your OAuth client ID, client secret, and the `AUTH_ID` (default: `google-drive-auth`).

### 5. Register with Gemini Enterprise

```bash
make register-gemini-enterprise
```

Use the `--authorization-id` flag to link the OAuth resource. The agent card now includes `securitySchemes` declaring the OAuth2 requirement.

### 6. IAM permissions

Grant the Discovery Engine service agent access to invoke Cloud Run:

```bash
gcloud projects add-iam-policy-binding <project-id> \
  --member="serviceAccount:service-<project-number>@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/run.servicesInvoker" \
  --condition=None --quiet
```

Note: Use `roles/run.servicesInvoker` at the **project level** (not `roles/run.invoker` at the service level).

### Alternative: Using Agent Starter Pack

You can also use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a production-ready version of this agent with additional deployment options:

```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-agent -a adk@adk-a2a-cr-oauth
```

<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and set up your project with a single command:
```bash
uvx agent-starter-pack create my-agent -a adk@adk-a2a-cr-oauth
```
This command handles creating the project without needing to pre-install the package into a virtual environment.

</details>

The starter pack will prompt you to select deployment options and provides additional production-ready features including automated CI/CD deployment scripts.

## Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make playground` | Launch ADK Web UI for local dev |
| `make local-backend` | Start FastAPI server with hot-reload |
| `make deploy` | Deploy to Cloud Run |
| `make register-oauth` | Register OAuth resource with Discovery Engine |
| `make register-gemini-enterprise` | Register agent with Gemini Enterprise |
| `make inspector` | Launch A2A Protocol Inspector |
| `make lint` | Run code quality checks |
| `make test` | Run unit and integration tests |

## Testing

```bash
# Start the local server
make local-backend

# Run the integration test (steps 1-2: agent card + A2A without OAuth)
uv run python tools/test_a2a_oauth.py

# Run all tests including Drive file read (needs a real file ID)
TEST_FILE_ID=<your-file-id> uv run python tools/test_a2a_oauth.py
```

## Security Considerations

- The service is `--allow-unauthenticated` at the Cloud Run level (required for Gemini Enterprise compatibility)
- App-level middleware validates every Bearer token's `aud`/`azp` against `OAUTH_CLIENT_ID`
- Agent card discovery endpoints are exempt from auth (required for A2A protocol)
- `--ingress=all` is required because Gemini Enterprise calls Cloud Run over the public internet
- Do not commit `OAUTH_CLIENT_SECRET` to the repo — use env vars or Secret Manager

---

## Troubleshooting

### `TenantProject` with location `global` does not exist (404)

This error occurs when trying to register an OAuth resource in a project where **Vertex AI Search and Conversation (Discovery Engine)** has not been initialized yet.
**Solution**: Go to the Google Cloud Console, navigate to **Vertex AI Search and Conversation**, and create a dummy Search or Chat app. This will trigger the creation of the internal tenant project and default collections.

### `authorizationConfig` missing after interactive registration

If you verify the registration and find that `authorizationConfig` is missing, the agent was registered without linking the OAuth credentials.
**Solution**: This can happen if the interactive `make register-gemini-enterprise` command skips the authorization ID. Delete the registration and use the non-interactive command (passing `AUTH_ID_RESOURCE` and other variables explicitly) to re-register.

### 404 Error on `/signin/` when clicking "Preview" in Console

If you get a 404 error pointing to `auth.cloud.google` when clicking the Preview button for your agent in the Gemini Enterprise console, this is likely a bug in the console's authentication routing for preview instances.
**Solution**: Your agent is likely configured correctly in the backend. Verify it using the `curl` command or API directly.
