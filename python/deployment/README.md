# Universal Agent Deployment Script

This directory contains a standalone set of tools to deploy ADK agents to **Vertex AI Agent Engine** and integrate them with **Gemini Enterprise (Discovery Engine)**.

## 📋 Prerequisites

1.  **Google Cloud Project**: You need a GCP project with billing enabled.
2.  **APIs Enabled**:
    *   `aiplatform.googleapis.com` (Vertex AI)
    *   `discoveryengine.googleapis.com` (Discovery Engine)
    *   `storage.googleapis.com` (Cloud Storage)
3.  **Python Environment**: Python 3.9+ recommended.
4.  **Permissions**: The user/service account running this script needs:
    *   `roles/aiplatform.user`
    *   `roles/discoveryengine.editor`
    *   `roles/storage.objectAdmin`
    *   `roles/iam.serviceAccountUser` (to act as the agent's service account)

## 🛠️ Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure `config.json`**:
    Copy the example config and fill in your details:
    ```bash
    cp config.json.example config.json
    ```

    | Field | Description | Required |
    | :--- | :--- | :--- |
    | `project_id` | Your Google Cloud Project ID. | Yes |
    | `project_number` | Your Google Cloud Project Number. | Yes |
    | `agent_path` | Path to your agent directory (e.g., `agents/my-agent` or `agents/my_agent`). | Yes |
    | `agent_module` | Python package name of your agent (e.g., `my_agent`). Required if `agent_path` directory name contains hyphens or differs from the package name. | Conditional |
    | `reasoning_engine_location` | Region for Vertex AI (e.g., `us-central1`). | Yes |
    | `reasoning_engine_agent_name` | Display name for the agent in Vertex AI. | Yes |
    | `reasoning_engine_agent_sa` | Service Account email for the agent to run as. | Yes |
    | `bucket` | Staging bucket name (created if not exists). | No (Optional) |

## 🔄 Full Integration Workflow

To get a fully functional agent in **Gemini Enterprise (Agent Space)**, follow these steps in order:

1.  **Deploy Agent**: Build and host the logic on Vertex AI.
    ```bash
    python deploy_agent.py deploy-agent --config config.json
    ```
2.  **Create Data Store**: Prepare the knowledge base (if you don't have one yet).
    ```bash
    python deploy_agent.py create-datastore --config config.json
    ```
3.  **Create Application**: Create the Agent Space "container".
    ```bash
    python deploy_agent.py create-app --config config.json
    ```
4.  **Link Agent**: Connect your Vertex AI logic to the Agent Space App.
    ```bash
    python deploy_agent.py link-agent --config config.json
    ```

---

## 🚀 Command Reference

### Agent Management (Vertex AI)

*   **Deploy/Update**: `deploy-agent`
    Builds the agent and deploys it to Vertex AI Agent Engine. Updates `config.json` with the new `reasoning_engine_id`.
*   **Delete**: `delete-agent`
    Removes the agent from Vertex AI.
*   **Test**: `test-agent`
    Interactive chat session to verify the deployed agent's logic.
*   **Build Only**: `build`
    Locally builds the agent wheels for manual inspection.

### Agent Space Management (Discovery Engine)

*   **Data Stores**: `create-datastore`, `list-datastores`
*   **Applications**: `create-app`, `update-app`, `delete-app`, `list-apps`
*   **Linking**: `link-agent`, `unlink-agent`, `list-linked-agents`, `rename-linked-agent`


## 🧹 Cleanup

To delete resources:

```bash
python deploy_agent.py delete-agent --config config.json
# python deploy_agent.py unlink-agent --config config.json
# python deploy_agent.py delete-app --config config.json
```

## 📦 Directory Structure

Recommended structure for your agent repository:

```text
.
├── agents/
│   └── my_agent/
│       ├── __init__.py
│       ├── agent.py       # Must define 'root_agent'
│       ├── .env           # Local env vars
│       └── requirements.txt
├── deployment/
│   ├── deploy_agent.py
│   ├── config.json
│   └── requirements.txt
└── ...
```
