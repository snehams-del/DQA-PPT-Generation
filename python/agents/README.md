# Sample Agents

This folder contains sample agent samples for
[Python Agent Development Kit](https://github.com/google/adk-python) (Python ADK).

Each folder in this directory contains a different agent sample.

## Getting Started

1.  **Prerequisites:**

    *   Python Agent Development Kit. See the
        [ADK Quickstart Guide](https://google.github.io/adk-docs/get-started/quickstart/).
    *   Python 3.9+ and [Poetry](https://python-poetry.org/docs/#installation).
    *   Access to Google Cloud (Vertex AI) and/or a Gemini API Key (depending on
        the agent - see individual agent READMEs).

2.  **Running a Sample Agent:**

    *   Navigate to the specific agent's directory (e.g., `cd agents/llm-auditor`).
    *    Copy the `.env.example` file to `.env` and fill in the required
         environment variables (API keys, project IDs, etc.). See the agent's
         specific README for details on required variables.
    *   Install dependencies using Poetry: `poetry install`
    *   Follow the instructions in the agent's `README.md` to run it (e.g.,
        using `adk run .` or `adk web`).


## Agent Categories

Check out the agent samples below, organized by category:

| Agent Name                                  | Use Case                                                                                                                              | Tag | Interaction Type | Complexity | Agent Type   | Vertical                      |
| :------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------- | :-: | :--------------- | :--------- | :----------- | :---------------------------- |
| [Agent Skills Tutorial](agent-skills-tutorial) | Demonstrates 4 ADK skill patterns: inline, file-based, external, and meta (skill-creator). Uses SkillToolset for progressive disclosure of skill metadata, instructions, and resources. | SkillToolset, Skills, Progressive disclosure | Conversational | Easy | Single Agent | Horizontal |
| [Academic Research](academic-research) | Assists researchers in identifying recent publications and discovering emerging research areas. |   Multi-agent, Custom tool, Evaluation | Workflow | Easy | Multi Agent | Academia                        |
| [Brand Search Optimization](brand-search-optimization) | Enrich e-commerce product data by analyzing and comparing top search results. Useful for addressing issues like "Null & low recovery" / "Zero Results" searches and identifies gaps in product data.                                 |   Multi-agent, Custom tool, BigQuery connection, Evaluation, Computer use   | Workflow | Easy | Multi Agent | Retail                        |
| [Cymbal Home & Garden Customer Service Agent](customer-service) | Customer service, product selection, order management for home improvement, gardening, and related supplies                                |  Custom tool, Async tool, External system calls, Live streaming, Multimodal   | Conversational         | Advanced     | Single Agent       | Retail                        |
| [Currency Agent](currency-agent) | Agent for currency exchange rate lookups and conversions. | Custom tool | Conversational | Intermediate | Single Agent | Financial Services |
| [Data Engineering Agent](data-engineering) | Data Engineering Agent designed for building sophisticated BigQuery and Dataform Pipelines                                                                          |  BigQuery, Dataform, ELT Pipelines, Data Curation, Data Modelling, Data Preperation, Data Ingestion, Analytics Engineering, Data Engineering   | Conversational | Advanced | Single Agent | Horizontal                    |
| [Data Science Agent](data-science) | A multi-agent system designed for sophisticated data analysis                                                                          |  Function tool (Python), Agent tool, NL2SQL, Structured data, Database   | Conversational | Advanced | Multi Agent | Horizontal                    |
| [Financial Advisor](financial-advisor) |  Assists human financial advisors by providing educational content about topics related to finance and investments.  |   Risk Analysis, Strategy Generation, Summarization, Report generation  | Workflow | Easy | Multi Agent | Financial Services            |
| [FOMC Research Agent](fomc-research) | Market event analysis                                                                                                                   |   Summarization, Report generation  | Workflow | Advanced | Multi Agent | Financial Services            |
| [Deep Search](deep-search) | A blueprint for building a sophisticated, fullstack research agent with Gemini. Demonstrates complex agentic workflows, modular agents, and Human-in-the-Loop (HITL) steps. | Multi-agent, Function calling, Web search, React frontend, FastAPI backend, Human-in-the-Loop | Workflow | Advanced | Multi Agent | Horizontal |
| [Gemma Food Tour Guide](gemma-food-tour-guide) | A food tour guide that uses Gemma 4 31B and Google Maps MCP to build personalized culinary tours from an image of a dish, location, and budget. | Tool calling, Google Maps MCP, Multimodal input, Route planning | LlmAgent | Intermediate | Single Agent | Travel and local discovery |
| [LLM Auditor](llm-auditor)                   | Chatbot Response Verification, Content Auditing                                                                                         |   Gemini with Google Search, Multi-agent  | Workflow         | Easy       | Multi Agent  | Horizontal                    |
| [Marketing Agency](marketing-agency)                   | Streamlines new website and product launches. Identifies optimal DNS domains, generates entire websites, develops marketing strategies, and designs brand assets. | Content generation, Website creation, Code generation, Strategy development  | Workflow         | Easy       | Multi Agent  | Horizontal                    |
| [Medical Pre-Authorization](medical-pre-authorization)                   | Automates the pre-authorization process by analyzing medical records and health policies to instantly determine coverage and eligibility. | Custom tool, Document Analysis, Report Generation  | Conversational         | Intermediate       | Multi Agent  | Healthcare                    |
| [Personalized Shopping](personalized-shopping) | Product Recommendations                                                                                                               | E-commerce, Personalized agent, Shopping assistant, Single-agent, Product recommendation, Product discovery, Chatbot    | Conversational         | Easy        | Single Agent     | E-commerce                    |
| [Vertex AI Retrieval Agent](RAG) | RAG Powered Agent / Answering questions related to documents uploaded to Vertex AI RAG Engine, providing informative responses with citations to source materials.                              |  RAG engine   | Workflow              | Intermediate        | Single Agent       | Horizontal                    |
| [Safety Guardrail Plugins](safety-plugins) | Safety filter plugins: Gemini as a judge, Model Armor as a filter                              |  Plugin, Security, Guardrail, Jailbreak, Multiagent   | Conversational/Workflow              | Intermediate        | Plugin       | Safety &Security                    |
| [Short Movie Agents](short-movie-agents) | Constructs end to end videos based on the user's intent. |   Multi-agent, Custom tool | Workflow | Intermediate | Multi Agent | Media           
| [Software Bug Assistant](software-bug-assistant)         | Assists in software bug resolution by querying internal ticketing systems and external knowledge sources (GitHub, StackOverflow, Google Search) to find similar issues and diagnostics. | RAG, MCP, Bug Tracking, Google Search, IT Support, Database Integration, API  | Workflow/Conversational | Intermediate | Single Agent | Horizontal / IT Support            |
| [Supply Chain](supply-chain)         | A multi-agent system designed to analyze real-time market dynamics, weather conditions, internal operations, and demand forecasts to optimize the power & energy supply chain. | Function tool (Python), Custom tool, Agent tool, Google Search, BigQuery  | Conversational | Intermediate | Multi Agent | Power & Energy (Supply Chain) 
| [Travel Concierge](travel-concierge) | Travel Concierge, Digital Tasks Assistant                                                                                               |   Function tool (Python), Custom tool, Agent tool, Input and output schema, Updatable context, Dynamic instructions  | Conversational | Advanced | Multi Agent | Travel                        |
| [YouTube Analyst](youtube-analyst) | Deep insights into YouTube content, channel performance, and audience engagement using interactive Plotly charts. | Multi-agent, YouTube API, Interactive charts | Conversational | Intermediate | Multi Agent | Marketing / Media Analytics |
| [Auto Insurance Agent](auto-insurance-agent) | Auto Insurance Agent to manage members, claims, rewards and roadside assistance.                                                                                              |   [Apigee](https://cloud.google.com/apigee/docs/api-platform/get-started/what-apigee), [Apigee API hub](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub), Agent Tool  | Conversational | Easy | Multi Agent | Financial Services       
| [Image Scoring](image-scoring) | Image scoring agent to generate images based on policies and score the generated images to measure policy compliance.  | Function tool (Python), Agent tool, Imagen, Loop Agent | Conversational | Easy       | Multi Agent  | Horizontal 
| [Antom Payment](antom-payment) | Integrates Ant International's Antom payment APIs to enable payment and refund operations via standardized MCP tools. | MCP, Payment, Refund, External API | Conversational | Intermediate | Single Agent | Financial Services / Payments
| [Incident Management](incident-management) | This agent sample showcases the utilization of dynamic identity propagation with ServiceNow and [Application Integration Connectors](https://cloud.google.com/application-integration/docs/using-integration-connectors)                                                                                              |   [Application Integration](https://cloud.google.com/application-integration/docs/overview), [Integration Connectors](https://cloud.google.com/integration-connectors/docs/overview), Agent Tool  | Conversational | Easy | Single Agent | Customer Support
| [Order Processing](order-processing) | This agent sample showcases how [Application Integration Connectors](https://cloud.google.com/application-integration/docs/using-integration-connectors) can be leveraged to automate orders and include human in the loop for workflows |   [Application Integration](https://cloud.google.com/application-integration/docs/overview), [Integration Connectors](https://cloud.google.com/integration-connectors/docs/overview), Agent Tool  | Conversational | Easy | Single Agent | Order Management
| [Google Trends Agent](google-trends-agent) | Surfaces top trending search trends from Google Trends using BigQuery dataset. Shows trending topics by region and time period. | BigQuery, Trend analysis, Sequential agent | Conversational | Medium | Sequential Agent | Marketing & Analytics |
| [Hierarchical Workflow Automation](hierarchical-workflow-automation) | The "Hierarchical Workflow Automation" pattern is an automation process where multiple distinct tasks or transactions must be executed in a structured hierarchy across various systems to complete a full workflow | Multi-agent, Custom tool, BigQuery, Agent Tool | Workflow | Advanced | Multi Agent / Sequential Agent | Order Management / Customer Support |
| [Plumber-Data-Engineering-Assistant](Plumber-Data-Engineering-Assistant) | A data engineering assistant agent capable of creating and deploy big data pipelines in Apache Spark, Apache Beam and dBT on GCP data stack via conversations | Big Data, Data Analytics, Streaming Analytics, Dataflow, Dataproc, Bigquery | Conversational | Hard | Multi Agent | Data & Analytics |
| [GenMedia for Commerce](genmedia-for-commerce) | Full-stack AI agent for commerce media generation: virtual try-on (image & video), 360° product spinning, background changing, product fitting, and catalogue search. Includes MCP server, FastAPI backend, React frontend, and Terraform infra. | MCP, Multimodal, Image generation, Video generation, Virtual try-on, Catalogue search, Agent Engine | Conversational | Advanced | Single Agent | Retail |
| [OpenRegistry · United Kingdom (Companies House)](openregistry-uk-companies-house) | United Kingdom company-data agent backed by live access to Companies House via the OpenRegistry MCP server. | MCP, Streamable HTTP, GB, KYC, KYB | Conversational | Easy | Single Agent | Compliance / United Kingdom |
| [OpenRegistry · Germany (Handelsregister)](openregistry-germany-handelsregister) | Germany company-data agent backed by live access to Handelsregister via the OpenRegistry MCP server. | MCP, Streamable HTTP, DE, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Germany |
| [OpenRegistry · France (RNE / Sirene)](openregistry-france-rne-sirene) | France company-data agent backed by live access to INSEE Sirene + RNE via the OpenRegistry MCP server. | MCP, Streamable HTTP, FR, KYC, KYB | Conversational | Easy | Single Agent | Compliance / France |
| [OpenRegistry · Italy (Registro Imprese (BRIS))](openregistry-italy-infocamere-bris) | Italy company-data agent backed by live access to Registro delle imprese (InfoCamere via EU BRIS) via the OpenRegistry MCP server. | MCP, Streamable HTTP, IT, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Italy |
| [OpenRegistry · Spain (BORME)](openregistry-spain-borme) | Spain company-data agent backed by live access to BORME — Boletín Oficial del Registro Mercantil via the OpenRegistry MCP server. | MCP, Streamable HTTP, ES, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Spain |
| [OpenRegistry · South Korea (OPENDART (전자공시))](openregistry-korea-opendart) | South Korea company-data agent backed by live access to OPENDART — 금융감독원 전자공시시스템 via the OpenRegistry MCP server. | MCP, Streamable HTTP, KR, KYC, KYB | Conversational | Easy | Single Agent | Compliance / South Korea |
| [OpenRegistry · Poland (KRS)](openregistry-poland-krs) | Poland company-data agent backed by live access to KRS — Krajowy Rejestr Sądowy via the OpenRegistry MCP server. | MCP, Streamable HTTP, PL, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Poland |
| [OpenRegistry · Netherlands (KVK)](openregistry-netherlands-kvk) | Netherlands company-data agent backed by live access to KVK Handelsregister via the OpenRegistry MCP server. | MCP, Streamable HTTP, NL, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Netherlands |
| [OpenRegistry · Belgium (KBO/BCE)](openregistry-belgium-kbo-bce) | Belgium company-data agent backed by live access to KBO/BCE — Crossroads Bank for Enterprises via the OpenRegistry MCP server. | MCP, Streamable HTTP, BE, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Belgium |
| [OpenRegistry · Ireland (CRO)](openregistry-ireland-cro) | Ireland company-data agent backed by live access to Companies Registration Office (CRO) via the OpenRegistry MCP server. | MCP, Streamable HTTP, IE, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Ireland |
| [OpenRegistry · Switzerland (Zefix)](openregistry-switzerland-zefix) | Switzerland company-data agent backed by live access to Zefix — Federal Registry of Commerce via the OpenRegistry MCP server. | MCP, Streamable HTTP, CH, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Switzerland |
| [OpenRegistry · Norway (Brreg)](openregistry-norway-brreg) | Norway company-data agent backed by live access to Brønnøysundregistrene (Enhetsregisteret) via the OpenRegistry MCP server. | MCP, Streamable HTTP, NO, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Norway |
| [OpenRegistry · Finland (PRH (YTJ))](openregistry-finland-prh) | Finland company-data agent backed by live access to PRH — Patentti- ja rekisterihallitus via the OpenRegistry MCP server. | MCP, Streamable HTTP, FI, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Finland |
| [OpenRegistry · Czechia (ARES)](openregistry-czechia-ares) | Czechia company-data agent backed by live access to ARES — Administrativní registr ekonomických subjektů via the OpenRegistry MCP server. | MCP, Streamable HTTP, CZ, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Czechia |
| [OpenRegistry · Australia (ABR / ASIC)](openregistry-australia-abr) | Australia company-data agent backed by live access to Australian Business Register (ABR — ABN Lookup) via the OpenRegistry MCP server. | MCP, Streamable HTTP, AU, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Australia |
| [OpenRegistry · New Zealand (NZ Companies Office)](openregistry-new-zealand-companies-office) | New Zealand company-data agent backed by live access to New Zealand Companies Office via the OpenRegistry MCP server. | MCP, Streamable HTTP, NZ, KYC, KYB | Conversational | Easy | Single Agent | Compliance / New Zealand |
| [OpenRegistry · Taiwan (GCIS (商工登記))](openregistry-taiwan-gcis) | Taiwan company-data agent backed by live access to GCIS — Ministry of Economic Affairs Commerce Department via the OpenRegistry MCP server. | MCP, Streamable HTTP, TW, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Taiwan |
| [OpenRegistry · Hong Kong SAR (HK CR)](openregistry-hong-kong-companies-registry) | Hong Kong SAR company-data agent backed by live access to Hong Kong Companies Registry (公司註冊處) via the OpenRegistry MCP server. | MCP, Streamable HTTP, HK, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Hong Kong SAR |
| [OpenRegistry · Malaysia (SSM)](openregistry-malaysia-ssm) | Malaysia company-data agent backed by live access to SSM — Suruhanjaya Syarikat Malaysia via the OpenRegistry MCP server. | MCP, Streamable HTTP, MY, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Malaysia |
| [OpenRegistry · Monaco (RCI Monaco)](openregistry-monaco-rci) | Monaco company-data agent backed by live access to RCI — Répertoire du Commerce et de l'Industrie via the OpenRegistry MCP server. | MCP, Streamable HTTP, MC, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Monaco |
| [OpenRegistry · Liechtenstein (Liechtenstein HR)](openregistry-liechtenstein-handelsregister) | Liechtenstein company-data agent backed by live access to Liechtenstein Handelsregister (Amt für Justiz) via the OpenRegistry MCP server. | MCP, Streamable HTTP, LI, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Liechtenstein |
| [OpenRegistry · Iceland (Fyrirtækjaskrá)](openregistry-iceland-fyrirtaekjaskra) | Iceland company-data agent backed by live access to Fyrirtækjaskrá — Skatturinn via the OpenRegistry MCP server. | MCP, Streamable HTTP, IS, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Iceland |
| [OpenRegistry · Cyprus (DRCOR Cyprus)](openregistry-cyprus-drcor) | Cyprus company-data agent backed by live access to DRCOR — Department of Registrar of Companies via the OpenRegistry MCP server. | MCP, Streamable HTTP, CY, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Cyprus |
| [OpenRegistry · Isle of Man (IoM CR)](openregistry-isle-of-man-companies-registry) | Isle of Man company-data agent backed by live access to Isle of Man Companies Registry via the OpenRegistry MCP server. | MCP, Streamable HTTP, IM, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Isle of Man |
| [OpenRegistry · Canada (Federal) (Corporations Canada)](openregistry-canada-cbca-federal) | Canada (Federal) company-data agent backed by live access to Corporations Canada (CBCA) via the OpenRegistry MCP server. | MCP, Streamable HTTP, CA, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Canada (Federal) |
| [OpenRegistry · Canada (British Columbia) (OrgBook BC)](openregistry-canada-bc-orgbook) | Canada (British Columbia) company-data agent backed by live access to BC Registries (OrgBook BC) via the OpenRegistry MCP server. | MCP, Streamable HTTP, CA-BC, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Canada (British Columbia) |
| [OpenRegistry · Canada (Northwest Territories) (CROS-RSEL NT)](openregistry-canada-nt-cros) | Canada (Northwest Territories) company-data agent backed by live access to CROS-RSEL — Corporate Registries Online (NT) via the OpenRegistry MCP server. | MCP, Streamable HTTP, CA-NT, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Canada (Northwest Territories) |
| [OpenRegistry · Mexico (PSM Mexico)](openregistry-mexico-psm) | Mexico company-data agent backed by live access to PSM — Sistema Electrónico de Publicaciones de Sociedades Mercantiles via the OpenRegistry MCP server. | MCP, Streamable HTTP, MX, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Mexico |
| [OpenRegistry · Cayman Islands (CIMA)](openregistry-cayman-cima) | Cayman Islands company-data agent backed by live access to CIMA — Cayman Islands Monetary Authority via the OpenRegistry MCP server. | MCP, Streamable HTTP, KY, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Cayman Islands |
| [OpenRegistry · Russia (ЕГРЮЛ (FNS))](openregistry-russia-egrul) | Russia company-data agent backed by live access to ЕГРЮЛ / ЕГРИП — Federal Tax Service via the OpenRegistry MCP server. | MCP, Streamable HTTP, RU, KYC, KYB | Conversational | Easy | Single Agent | Compliance / Russia |



## Using the Agents in this Repository

This section provides general guidance on how to run, test, evaluate, and potentially deploy the agent samples found in this repository. While the core steps are similar, **each agent has its own specific requirements and detailed instructions within its dedicated `README.md` file.**

**Always consult the `README.md` inside the specific agent's directory (e.g., `agents/fomc-research/README.md`) for the most accurate and detailed steps.**

Here's a general workflow you can expect:

1.  **Choose an Agent:** Select an agent from the table above that aligns with your interests or use case.
2.  **Navigate to the Agent Directory:** Open your terminal and change into the
    agent's main directory from the main repo directory:
    ```bash
    cd python/agents/<agent-name>
    # Example: cd python/agents/fomc-research
    ```
3.  **Review the Agent's README:** **This is the most crucial step.** Open the
    `README.md` file within this directory. It will contain:
    *   A detailed overview of the agent's purpose and architecture.
    *   Specific prerequisites (e.g., API keys, cloud services, database setup).
    *   Step-by-step setup and installation instructions.
    *   Commands for running the agent locally.
    *   Instructions for running evaluations (if applicable).
    *   Instructions for running tests (if applicable).
    *   Steps for deployment (if applicable).

4.  **Setup and Configuration:**
    *   **Prerequisites:** Ensure you've met the general prerequisites listed in
        the main "Getting Started" section *and* any specific prerequisites
        mentioned in the agent's README.
    *   **Dependencies:** Install the agent's specific Python dependencies using
        Poetry (this command is usually run from the agent's main directory):
        ```bash
        poetry install
        ```
    *   **Environment Variables:** Most agents require configuration via
        environment variables. Copy the `.env.example` file to `.env` within the
        agent's directory and populate it with your specific values (API keys,
        project IDs, etc.). Consult the agent's README for details on required
        variables. You may need to load these variables into your shell
        environment (e.g., using `source .env` or `set -o allexport; . .env; set
        +o allexport` in bash).

5.  **Running the Agent Locally:**
    *   Agents can typically be run locally for testing and interaction using
        the ADK CLI or ADK Dev UI. The specific command might vary slightly
        (e.g., the exact directory to run from), so check the agent's README.
        **CLI:** Often involves running `adk run .` from within the agent's
        *core code* directory (e.g., `agents/fomc-research/fomc_research/`).
        ```bash
        # Example (check agent's README for exact path)
        cd agents/fomc-research/fomc_research/
        adk run .
        ```
    *   **ADK Dev UI:** Often involves running `adk web .` from the agent's
        *main* directory (e.g., `agents/fomc-research/`).
        ```bash
        # Example (check agent's README for exact path)
        cd agents/fomc-research/
        adk web
        ```
        Then, open the provided URL in your browser and select the agent from the dropdown menu.

6.  **Evaluating the Agent:**
    *   Many agents include an `eval/` directory containing scripts and data to assess performance.
    *   The agent's README will explain how to run these evaluations (e.g.,
        `python eval/test_eval.py`). This helps verify the agent's effectiveness
        on specific tasks.

7.  **Testing the Agent Components:**
    *   A `tests/` directory often contains unit or integration tests (e.g., for custom tools).
    *   These ensure the individual code components function correctly.
    *   The agent's README may provide instructions on how to run these tests,
        often using a framework like `pytest`.

8.  **Deploying the Agent:**
    *   Some agents are designed for deployment, typically to
        [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview).
    *   The `deployment/` directory contains the necessary scripts (like
        `deploy.py`) and configuration files.
    *   Deployment usually requires specific Google Cloud setup (Project ID,
        enabled APIs, permissions). The agent's README and the scripts within
        the `deployment/` folder provide detailed instructions, similar to the
        example shown in the `fomc-research` agent's documentation.

By following the specific instructions in each agent's `README.md`, you can effectively set up, run, evaluate, test, and potentially deploy these diverse examples.

## Directory Structure of Agents
Each agent displayed here is organized as follows:

```bash
├── agent-name
│   ├── agent_name/
│   │   ├── shared_libraries/               # Folder contains helper functions for tools
│   │   ├── sub_agents/                     # Folder for each sub agent
│   │   │   │   ├── tools/                  # tools folder for the subagent
│   │   │   │   ├── agent.py                # core logic of the sub agent
│   │   │   │   └── prompt.py               # prompt of the subagent
│   │   │   └── ...                         # More sub-agents
│   │   ├── __init__.py                     # Initializes the agent
│   │   ├── tools/                          # Contains the code for tools used by the router agent
│   │   ├── agent.py                        # Contains the core logic of the agent
│   │   ├── prompt.py                       # Contains the prompts for the agent
│   ├── deployment/                         # Deployment to Agent Engine
│   ├── eval/                               # Folder containing the evaluation method
│   ├── tests/                              # Folder containing unit tests for tools
│   ├── agent_pattern.png                   # Diagram of the agent pattern
│   ├── .env.example                        # Store agent specific env variables
│   ├── pyproject.toml                      # Project configuration
│   └── README.md                           # Provides an overview of the agent
```
### General Structure

The root of each agent resides in its own directory under `agents/`. For example, the `llm-auditor` agent is located in `agents/llm-auditor/`.


#### Directory Breakdown

1.  **`agent_name/` (Core Agent Code)**:
    *   This directory contains the core logic of the agent.
    *   **`shared_libraries/`**: (Optional) Contains code that is shared among multiple sub-agents.
    *   **`sub_agents/`**: Contains the definitions and logic for sub-agents.
        *   Each sub-agent has its own directory (e.g., `critic/`, `reviser/` in `llm-auditor`).
        *   **`tools/`**: Contains any custom tools specific to the sub-agent.
        *   **`agent.py`**: Defines the sub-agent's behavior, including its model, tools, and instructions.
        *   **`prompt.py`**: Contains the prompts used to guide the sub-agent's behavior.
    *   **`__init__.py`**: An initialization file that imports the `agent.py` from the folder for marking the `agent_name` directory as a Python package.
    *   **`tools/`**: Contains any custom tools used by the main agent.
    *   **`agent.py`**: Defines the main agent's behavior, including its sub-agents, model, tools, and instructions.
    *   **`prompt.py`**: Contains the prompts used to guide the main agent's behavior.

    Note that the initial folder name is with "-" between words whereas the core logic is stored in the folder with the same agent name but with "_" between words (e.g., `llm_auditor`). This is due to the project structure imposed by poetry.

2.  **`deployment/`**

    *   Contains scripts and files necessary for deploying the agent to a
        platform like Vertex AI Agent Engine.
    *   The `deploy.py` script is often found here, handling the deployment process.

3.  **`eval/`**

    *   Contains data and scripts for evaluating the agent's performance.
    *   Test data (e.g., `.test.json` files) and evaluation scripts (e.g.,
        `test_eval.py`) are typically located here.

4.  **`tests/`**

    *   Contains unit and integration tests for the agent.
    *   Test files (e.g., `test_agents.py`) are used to verify the agent's functionality.

5.  **`agent_pattern.png`**

    *   A visual diagram illustrating the agent's architecture, including its sub-agents and their interactions.

6.  **`.env.example`**

    *   An example file showing the environment variables required to run the agent.
    *   Users should copy this file to `.env` and fill in their specific values.

7.  **`pyproject.toml`**

    *   Contains project metadata, dependencies, and build system configuration.
    *   Managed by Poetry for dependency management.

8.  **`README.md`**

    *   Provides detailed documentation specific to the agent, including its purpose, setup instructions, usage examples, and customization options.

## Example: `llm-auditor`

The `llm-auditor` agent demonstrates this structure effectively. It has:

*   A core `llm_auditor/` directory.
*   Sub-agents in `llm_auditor/sub_agents/`, such as `critic/` and `reviser/`.
*   Deployment scripts in `deployment/`.
*   Evaluation data and scripts in `eval/`.
*   Tests in `tests/`.
*   An `.env.example` file.
*   A `pyproject.toml` file.
*   A `README.md` file.
