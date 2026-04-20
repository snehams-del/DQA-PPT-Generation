# A2A - ADK - Accessing User Permitted Files

This project demonstrates an agent built with Google's Agent Development Kit (ADK) (and deployed on Cloud Run) that can interact with Google Cloud Storage (GCS) to list folder contents for which user has permission. A key feature of this sample is its integration with the Agent-to-Agent (A2A) framework, specifically showcasing how user authentication tokens from incoming A2A requests can utilized by ADK tools.

## Features

*   **GCS Folder Listing:** An ADK Agent can list files and subfolders within a specified Google Cloud Storage (GCS) path (e.g., `gs://bucket-name/folder/`).
*   **A2A Authentication Forwarding:** The sample demonstrates how to use an `Authorization` from an incoming A2A request's `RequestContext` (e.g., from Agent Integrated in Gemini Enterprise as A2A Agent), and use authorised information to create authenticated Google Cloud client access within ADK Agent tools. This enables the agent to perform actions on GCS on behalf of the end-user.
*   **Google ADK Integration:** Leverages the `google.adk` library for defining the agent, utilizing the Gemini model.
*   **A2A Server Integration:** Uses the `a2a.server` components for handling agent execution requests, managing tasks, and exposing the agent via a standard A2A endpoint.

## Prerequisites

Before running this agent, ensure you have the following:

*   **Python:** Version 3.13 or newer.
*   **uv:** (latest version)
*   **Google Cloud SDK (`gcloud`):** Installed and configured with authentication to your Google Cloud Project. 
*   **Google Cloud Project:** A Google Cloud Project with necessary permissions.


## Installation

1.  **Clone the repository:**
    ```bash
    # git clone https://github.com/google/adk-samples.git
    # cd adk-samples/python/agents/a2a-adk-auth
    ```
2.  **Install dependencies:**
    ```bash
    uv sync
    ```

## Deploying and running the Agent

The agent runs as a FastAPI application using Uvicorn.

```bash
gcloud auth application-default login
gcloud config set project <gcp-project>

export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export REGION=us-central1

export APP_URL="http://0.0.0.0:8000"

# For Cloud Run can use below APP_URL
# export APP_NAME=app_name # provide your app name
# export APP_URL="https://${APP_NAME}-${PROJECT_NUMBER}.${REGION}.run.app"

export TOKEN=$(gcloud auth print-access-token)
```

### Running the Agent
```bash
uv run app/main.py
```

For Deploying on Cloud Run:
```bash
gcloud beta run deploy ${APP_NAME} \
--source . \
--memory "4Gi" \
--project ${PROJECT_ID} \
--region "us-central1" \
--no-allow-unauthenticated \
--no-cpu-throttling \
--update-env-vars \
"APP_URL=https://tutorial-${PROJECT_NUMBER}.${REGION}.run.app"
```

Once running, the agent will be accessible via its A2A endpoint.
```bash
curl -X GET \
$APP_URL/a2a/app/.well-known/agent-card.json \
-H "Authorization: Bearer $TOKEN"

curl -X POST \
$APP_URL/a2a/app \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "jsonrpc": "2.0",
  "method": "message/send",
  "params": {
    "message": {
      "messageId": "some-unique-id",
      "role": "user",
      "parts": [
        {
          "text": "Please list the contents of the GCS path gs://<bucket>/<folder>/"
        }
      ]
    }
  },
  "id": "1"
}'
```

## Usage

This agent is designed to be interacted with via an A2A client or another A2A-compatible service.

The agent's `list_gcs_folder` tool will extract this token from the A2A `RequestContext` and use it to authenticate Google Cloud Storage API calls.

**Example Interaction (Conceptual):**

Assume you have an A2A client capable of sending requests to the agent.
*   **User Prompt:** "list the contents of gs://my-example-bucket/my-folder/"
*   **A2A Request:** The client would send a request to the agent's A2A endpoint.
*   **Agent Response:** The agent would use its `list_gcs_folder` tool, authenticated with users access, to list the contents of `my-example-bucket/my-folder/` and return the formatted output.

PS: 
You can integrate Agent Deployed on Cloud Run with Gemini Enterprise by following steps from https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-a2a-agent

Curl commands provided above will simulate behaviour of Gemini Enterprise Integration.

## Project Structure

*   `app/agent.py`: Contains the definition of the ADK `root_agent`, the Gemini model configuration, and the `list_gcs_folder` tool implementation.
*   `app/agent_executor.py`: Provides a `CustomAgentExecutor` responsible for integrating with the A2A server, managing ADK sessions.
*   `app/main.py`: Sets up the FastAPI application, initializes the ADK `Runner` and A2A `DefaultRequestHandler`, and defines the application's lifecycle, including dynamic agent card generation.
*   `pyproject.toml`: Specifies project metadata and Python dependencies.
