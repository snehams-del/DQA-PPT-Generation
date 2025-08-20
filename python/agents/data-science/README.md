# Data Science with Multiple Agents

## Overview

This project demonstrates a multi-agent system designed for sophisticated data analysis. It integrates several specialized agents to handle different aspects of the data pipeline, from data retrieval to advanced analytics and machine learning. The system is built to interact with BigQuery, perform complex data manipulations, generate data visualizations and execute machine learning tasks using BigQuery ML (BQML). The agent can generate text response as well as visuals, including plots and graphs for data analysis and exploration.

▶️ **Watch the Video Walkthrough:** [How to build a Data Science agent with ADK](https://www.youtube.com/watch?v=efcUXoMX818)

## Agent Details
The key features of the Data Science Multi-Agent include:

| Feature | Description |
| --- | --- |
| **Interaction Type:** | Conversational |
| **Complexity:**  | Advanced |
| **Agent Type:**  | Multi Agent |
| **Components:**  | Tools, AgentTools, Session Memory, RAG |
| **Vertical:**  | All (Applicable across industries needing advanced data analysis) |


### Architecture
![Data Science Architecture](data-science-architecture.png)

### Key Features

*   **Multi-Agent Architecture:** Utilizes a top-level agent that orchestrates sub-agents, each specialized in a specific task.
*   **Database Interaction (NL2SQL):** Employs a Database Agent to interact with BigQuery using natural language queries, translating them into SQL.
*   **Data Science Analysis (NL2Py):** Includes a Data Science Agent that performs data analysis and visualization using Python, based on natural language instructions.
*   **Machine Learning (BQML):** Features a BQML Agent that leverages BigQuery ML for training and evaluating machine learning models.
*   **Code Interpreter Integration:** Supports the use of a Code Interpreter extension in Vertex AI for executing Python code, enabling complex data analysis and manipulation.
*   **ADK Web GUI:** Offers a user-friendly GUI interface for interacting with the agents.
*   **Testability:** Includes a comprehensive test suite for ensuring the reliability of the agents.



## Setup and Installation

### Prerequisites

*   **Google Cloud Account:** You need a Google Cloud account with BigQuery enabled.
*   **Python 3.12+:** Ensure you have Python 3.12 or a later version installed.
*   **uv:** Install uv by following the instructions on the official uv website: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
*   **Git:** Ensure you have git installed. If not, you can download it from [https://git-scm.com/](https://git-scm.com/) and follow the [installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
*   **Terraform** >= 1.0 installed ([installation guide](https://learn.hashicorp.com/tutorials/terraform/install-cli))
*   **Google Cloud SDK** configured with authentication



### Project Setup with uv

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/data-science
    ```

2.  **Configure Google Cloud Project:**

    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```
    
    Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

3.  **Install Dependencies with uv:**

    ```bash
    uv sync
    ```

    This command reads the `pyproject.toml` file and installs all the necessary
    dependencies into a virtual environment managed by uv. On the first run,
    this command will also create a new virtual environment. By default, the
    virtual environment will be created in a `.venv` directory inside
    `adk-samples/python/agents/data-science`. If you already have a virtual
    environment created, or you want to use a different location, you can use
    the `--active` flag for `uv` commands, and/or change the
    `UV_PROJECT_ENVIRONMENT` environment variable. See
    [How to customize uv's virtual environment location](https://pydevtools.com/handbook/how-to/how-to-customize-uvs-virtual-environment-location/)
    for more details.

4.  **Deploy Infrastructure with Terraform:**

    ```bash
    make deploy-infra
    ```
    
    **Advanced Configuration (Optional):** For custom configuration options, copy `infra/vars/env.tfvars.example` to `infra/vars/env.tfvars`, edit your settings, and use `terraform apply --var-file vars/env.tfvars`.

    This will automatically provision all required GCP resources including:
    - BigQuery dataset and tables with sample data
    - Vertex AI RAG corpus for BQML documentation
    - Code Interpreter extension
    - Cloud Storage staging bucket
    - Cloud Storage bucket for Terraform state management
    - Required API enablement and IAM permissions

    **For detailed Terraform configuration options and troubleshooting, see [infra/README.md](infra/README.md).**

4.  **Environment Variables (Optional):**

    The agent automatically detects your Google Cloud project and uses sensible defaults for all configuration. **No environment variables are required** if you're using the default setup.
    
    If you need to customize the configuration, you can create a `.env` file in the `/data_science` folder.

    <details>
    <summary>📋 Common customizable variables</summary>
    
    ```bash
    # Optional: Override auto-detected project
    GOOGLE_CLOUD_PROJECT=your-project-id
    
    # Optional: Override auto-detected location  
    GOOGLE_CLOUD_LOCATION=us-central1
    
    # Optional: Override auto-detected bucket
    GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
    
    # Optional: Custom BigQuery dataset
    BIGQUERY_DATASET_ID=your-dataset-name
    ```
    </details>

    For our sample use case, we are working on the Forecasting Sticker Sales data from Kaggle:
    _Walter Reade and Elizabeth Park. Forecasting Sticker Sales. https://kaggle.com/competitions/playground-series-s5e1, 2025. Kaggle._


## Development Workflow

### Running the Agent Locally

You can run the agent using the ADK command in your terminal.
from the working directory:

1.  Run agent in CLI:

    ```bash
    uv run adk run data_science
    ```

2.  Run agent with ADK Web UI:
    ```bash
    uv run adk web
    ```
    Select the data_science from the dropdown

### Code Quality and Testing

The project includes a Makefile with common development tasks:

**Install all dependencies (including dev dependencies):**
```bash
make install
```

**Run code quality checks:**
```bash
make lint
```
This runs codespell, ruff linting, formatting checks, and mypy type checking.

**Run tests:**
```bash
make test
```

**Run evaluations:**
```bash
make eval
```

**Launch playground UI:**
```bash
make playground
```
This starts the ADK web interface on port 8501.



### Example Agent Interaction

Here's a quick example of how a user might interact with the Data Science Multi-Agent System:

> ´**User:** Hi, What data do you have access to?

> **Agent:**  I have access to two tables: `train` and `test`. Both tables contain sticker sales data with the following columns: `id`, `date`, `country`, `store`, `product`, and `num_sold`.

> **User:** I need more details on the train table. What countries exist? How many stores are there?

> **Agent:** Result: The train table contains data from Canada, Finland, Italy, Kenya, Norway, and Singapore. Each of these countries has 3 distinct stores.

>Explanation: The database agent executed a SQL query against the train table to find the distinct countries and the number of distinct stores within each country. The query grouped the results by country and counted the distinct store values.

> **User:** Please generate a plot with total sales per country.

> **Agent:**  Result: A bar plot has been generated showing the total sales per country. The x-axis represents the country, and the y-axis represents the total sales.

> Explanation:
> 1. The database agent was first called to retrieve the total sales per country from the train table.
> 2. The data science agent was then called to generate a bar plot visualizing the results. The plot displays each country on the x-axis and its corresponding total sales on the y-axis.

> **User:** What kinds of forecasting models can I train in BQML?

> **Agent:** You can train several types of forecasting models in BQML, including ARIMA, Exponential Smoothing, and Temporal Fusion Transformer (TFT) models. Would you like to proceed with training a forecasting model?

> **User:** Yes

> **Agent:** Okay, before proceeding, let's confirm the project and dataset ID for BQML. We'll be using the `PROJECT_ID` project and the `forecasting_sticker_sales` dataset. Does that sound right?

> **User:** Yes

> **Agent:** The BQML supports `ARIMA_PLUS`, `ARIMA_PLUS_XREG`.

>To proceed, I need to know which model you'd like to use. I also need to know the following:

>*   The name of the column that provides the time points (e.g., 'date').
>*   The name of the column that contains the data to forecast (e.g., 'num_sold').
>*   Do you want to fit and forecast multiple time series using a single query? If so, what are the ID columns? (e.g., `country`, `store`, `product`)


## Testing and Evaluation

To run the test and evaluation code, you need a few additional dependencies. Run
the following uv command from the `agents/data-science` directory to install them:
```bash
uv sync --extra dev
```

### Running Evaluations


Evaluation tests assess the overall performance and capabilities of the agent in a holistic manner.

**Run Evaluation Tests:**

```bash
uv run pytest eval
```

- This command executes all test files within the `eval/` directory.
- `uv run` ensures that pytest runs within the project's virtual environment.


## ☁️ Cloud Deployment

Once you setup Terraform, you have multiple options for deploying this agent to Google Cloud. Choose the approach that best fits your needs.

### Option 1: ADK Command Line Deployment

The simplest way to deploy your agent is using the ADK command line tools directly:

**Prerequisites:**
- **[Google Cloud SDK](https://cloud.google.com/sdk/docs/install)** configured with authentication
- **Google Cloud Project** with the **Vertex AI API** enabled
- Terraform infrastructure already deployed (see Setup section above)

**Deploy to Agent Engine:**
```bash
# From the project root directory
uv run adk deploy agent_engine
```

After successful deployment, the command will output a resource ID. Save this for testing your deployed agent.

**Deploy to Cloud Run:**
```bash
# From the project root directory  
uv run adk deploy cloud_run
```

After successful deployment, the command will output a service URL where your agent is accessible.

These commands will automatically package your agent and deploy it to the specified platform using your existing Google Cloud configuration.

#### Testing Your Deployed Agent

**For Agent Engine deployments:**
Use the test script with your deployed resource ID:
```bash
uv run python tests/test_deployment.py --resource_id=YOUR_RESOURCE_ID --user_id=test_user
```

This will start an interactive session where you can test your deployed agent. Type 'quit' to exit.

**For Cloud Run deployments:**
Your agent will be available at the provided service URL and can be tested through the web interface or API calls.

### Option 2: Agent Starter Pack (Full Project Template)

If you prefer a complete project template with CI/CD and additional tooling, you can use the [Agent Starter Pack](https://goo.gle/agent-starter-pack):

#### Step 1: Create Project from Template
This command uses the Agent Starter Pack to create a new directory with all the necessary deployment code.
```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-data-science-agent -a adk@data-science
```

<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and set up your project with a single command:
```bash
uvx agent-starter-pack create my-data-science-agent -a adk@data-science
```
This command handles creating the project without needing to pre-install the package into a virtual environment.
</details>

You'll be prompted to select a deployment option (Agent Engine or Cloud Run) and verify your Google Cloud credentials.

#### Step 2: Deploy to Development Environment
Navigate into your **newly created project folder**, then deploy to a development environment:
```bash
cd my-data-science-agent

# Replace YOUR_DEV_PROJECT_ID with your actual Google Cloud Project ID
gcloud config set project YOUR_DEV_PROJECT_ID
make backend
```

For robust, **production-ready deployments** with automated CI/CD, please follow the detailed instructions in the **[Agent Starter Pack Development Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html#b-production-ready-deployment-with-ci-cd)**.



### Running Tests

Tests assess the overall executability of the agents.

**Test Categories:**

*   **Integration Tests:** These tests verify that the agents can interact correctly with each other and with external services like BigQuery. They ensure that the root agent can delegate tasks to the appropriate sub-agents and that the sub-agents can perform their intended tasks.
*   **Sub-Agent Functionality Tests:** These tests focus on the specific capabilities of each sub-agent (e.g., Database Agent, BQML Agent). They ensure that each sub-agent can perform its intended tasks, such as executing SQL queries or training BQML models.
*   **Environment Query Tests:** These tests verify that the agent can handle queries that are based on the environment.

**Run Tests:**

```bash
uv run pytest tests/integration
```

- This command executes all test files within the `tests/` directory.
- `uv run` ensures that pytest runs within the project's virtual environment.


## Optimizing and Adjustment Tips

*   **Prompt Engineering:** Refine the prompts for `root_agent`, `bqml_agent`, `db_agent`
    and `ds_agent` to improve accuracy and guide the agents more effectively.
    Experiment with different phrasing and levels of detail.
*   **Extension:** Extend the multi-agent system with your own AgentTools or sub_agents.
    You can do so by adding additional tools and sub_agents to the root agent inside
    `agents/data-science/data_science/agent.py`.
*   **Partial imports:** If you only need certain capabilities inside the multi-agent system,
    e.g. just the data agent, you can import the data_agent as an AgentTool into your own root agent.
*   **Model Selection:** Try different language models for both the top-level
    agent and the sub-agents to find the best performance for your data and
    queries.


## Troubleshooting

*   If you face `500 Internal Server Errors` when running the agent, simply re-run your last command.
    That should fix the issue.
*   If you encounter issues with the code interpreter, review the logs to
    understand the errors. Make sure you're using base-64 encoding for
    files/images if interacting directly with a code interpreter extension
    instead of through the agent's helper functions.
*   If you see errors in the SQL generated, try the following:
    - including clear descriptions in your tables and columns help boost performance
    - if your database is large, try setting up a RAG pipeline for schema linking by storing your table schema details in a vector store


## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations, and does not include features or optimizations typically required for a production environment (e.g., robust error handling, security measures, scalability, performance considerations, comprehensive logging, or advanced configuration options).

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.
