# nurse-handover

## Overview

This project uses Google Cloud's Gemini generative AI model to create concise and informative nurse handover summaries from detailed medical records. It streamlines the handover process, reducing the risk of miscommunication and improving patient safety.

## Agent Details

### Key Features

- **Automated Summary Generation:** Generates nurse handover summaries automatically from input medical records.
- **ISBAR Format:** Structures summaries using the ISBAR (Identification, Situation, Background, Assessment, Recommendation) format for clear and consistent communication.
- **Shift-Based Summaries:** Generates summaries for specific shifts, ensuring relevant information is readily available.
- **Retry Mechanism:** Includes a retry mechanism for handling transient errors during API calls.
- **Input Validation:** Validates input parameters to ensure data integrity.

### Architecture

The system consists of the following key components:

1. **List Patients:** List current patients of the identified nurse.
1. **List Shifts:** List shifts available for endorsement generation for the identified nurse.
1. **Summary Generator:** Orchestrates the summary generation process. Retrieves the relevant medical record, filters irrelevant information, interacts with the Gemini API, and formats the summary into a markdown file.

### Example Agent Interaction

**User:** Hi!

**Assistant:** Hello! I'm your nurse shift handover assistant. My purpose is to help streamline your shift handover process by automatically generating comprehensive reports. (Calls patient and shift lookup tools...) I can generate a shift endorsement for patient **MHID123456789** for the shift that started on **2024-06-07T07:30:00** and ended on **2024-06-07T19:30:00**. Would you like me to go ahead and generate the report for you?

**User:** Yes, please!

**Assistant:** (Calls endorsement generation tool...) I have stored the following artifacts: (1) raw patient input file at `MHID123456789-1717763400-1717806600-raw-inputs.txt` and (2) the endorsement report at `MHID123456789-1717763400-1717806600-endorsement.md`.

## Setup and Installation

### Prerequisites

- **Google Credentials:** You need a GCP project _or_ Gemini API key for local testing. You need a GCP project for deployment to Cloud Run.
- **UV:** Ensure that you have uv installed. If you don't already, please follow the installation instructions at [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/).

### Project Setup

1. **Install dependencies in a virtual environment:**

```bash
uv sync --dev
```

2. **Set up Environment Variables:** Create a file named `.env` and update values as needed.

```bash
# If using API key: ML Dev backend config.
GOOGLE_API_KEY=YOUR_VALUE_HERE
GOOGLE_GENAI_USE_VERTEXAI=false

# If using Vertex on GCP: Vertex backend config
GOOGLE_CLOUD_PROJECT=YOUR_VALUE_HERE
GOOGLE_CLOUD_LOCATION=YOUR_VALUE_HERE
GOOGLE_GENAI_USE_VERTEXAI=true

AGENT_MODEL_NAME=gemini-2.5-flash
SECTION_MODEL_NAME=gemini-2.5-flash
SUMMARY_MODEL_NAME=gemini-2.5-flash
```

3. **If you're using a GCP project, authenticate with GCP and enable VertexAI:**

```bash
gcloud auth login --update-adc
gcloud config set project PROJECT_ID
gcloud services enable aiplatform.googleapis.com
```

You are now ready to start development on your project!

### Alternative: Using Agent Starter Pack

You can also use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a production-ready version of this agent with additional deployment options:

```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-nurse-handover -a adk@nurse-handover
```

<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and set up your project with a single command:
```bash
uvx agent-starter-pack create my-nurse-handover -a adk@nurse-handover
```
This command handles creating the project without needing to pre-install the package into a virtual environment.

</details>

The starter pack will prompt you to select deployment options and provides additional production-ready features including automated CI/CD deployment scripts.

## Running the Agent

Run the agent(s) API server with the command: `uv run start`

Run the agent with the ADK Web UI with the command: `uv run web`

## Running Tests

Tests assess the overall executability of the agents. All tests are located under the `tests/` directory.

Run tests with the command `make test`
