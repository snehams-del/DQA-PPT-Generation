# Data Engineering Agent

A comprehensive data engineering agent.

## Features

- **Dataform Pipeline Development**
  - Build and modify Dataform pipelines
  - Create and update SQLx files
  - Handle UDFs and stored procedures integration
  - Manage table schemas and data types

- **Dataform Troubleshooting**
  - Diagnose pipeline issues
  - Analyze execution logs
  - Fix compilation errors
  - Optimize pipeline performance

- **Data Engineering**
  - Design and implement data transformations
  - Handle complex SQL queries
  - Manage data dependencies
  - Ensure data quality

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root directory:
   ```bash
   cp .env.example .env
   ```
4. Edit the `.env` file with your configuration:
   ```ini
   # Google Cloud Configuration
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1  # Used for Vertex AI, Dataform, and BigQuery
   GOOGLE_GENAI_USE_VERTEXAI=1

   # Model Configuration
   ROOT_AGENT_MODEL=gemini-2.5-pro
   DOCS_AGENT_MODEL=gemini-2.0-flash

   # Dataform Configuration
   DATAFORM_REPOSITORY_NAME=your-repository-name
   DATAFORM_WORKSPACE_NAME=your-workspace-name
   ```

## Configuration

The agent can be configured using:
1. Environment variables in the `.env` file
2. Command-line arguments (which override .env values)

### Environment Variables
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID (preferred) or use `GCP_PROJECT_ID`
- `GOOGLE_CLOUD_LOCATION`: Location for Vertex AI, Dataform, and BigQuery (default: us-central1)
- `GOOGLE_GENAI_USE_VERTEXAI`: Set to 1 to use Vertex AI (default: 0)
- `ROOT_AGENT_MODEL`: Model to use for the root agent (default: gemini-2.5-pro-preview-05-06)
- `DATAFORM_REPOSITORY_NAME`: Your Dataform repository name
- `DATAFORM_WORKSPACE_NAME`: Your Dataform workspace name


5- Run ADK from the upper folder:
  ```bash
   cd ..
   adk web
   ```
  or 

~~~bash
   adk run
   ```

# License
   Copyright 2025 Google LLC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
~~~
