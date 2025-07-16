# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python Development

**Package Management:**
```bash
# uv (preferred for newer agents like software-bug-assistant, gemini-fullstack)
uv sync
uv run <command>

# Poetry (used by older agents like RAG, data-science)
poetry install
poetry run <command>
```

**Running Agents:**
```bash
# CLI mode (from agent directory)
adk run .

# Web UI mode (from agent directory)  
adk web

# API server mode (for fullstack agents)
adk api_server app --allow_origins="*"

# Web playground mode
adk web --port 8501
```

**Linting and Formatting:**
```bash
# Modern Python stack (preferred)
ruff check . --diff
ruff format . --check --diff
mypy .
codespell

# Legacy tools (some older agents)
black .
pylint .
flake8 .
```

**Testing:**
```bash
# Standard testing
pytest
pytest -vv -s
pytest --cov

# Run specific test file or pattern
pytest tests/test_agents.py
pytest tests/unit/
```

**Evaluation:**
```bash
# Run agent evaluation with test data
adk eval <agent_name> eval/data/eval_data.evalset.json --config_file_path eval/data/test_config.json
```

### Java Development

**Building:**
```bash
mvn clean compile
mvn clean install
```

**Testing:**
```bash
mvn test
```

**Running Agents:**
```bash
# Execute main class directly
mvn exec:java

# ADK Dev UI with custom port
mvn compile exec:java -Dexec.args="--server.port=8080"
```

### Fullstack Development (gemini-fullstack only)

**Using Makefile:**
```bash
make install        # Install all dependencies (uv + npm)
make dev           # Run both frontend and backend concurrently
make dev-backend   # Backend only: adk api_server
make dev-frontend  # Frontend only: npm run dev
make playground    # Web UI: adk web --port 8501
make lint          # Full linting suite
```

## Repository Architecture

### High-Level Structure

This repository contains **Agent Development Kit (ADK) samples** demonstrating various AI agent patterns:

- **`/python/agents/`** - 18 Python-based agents across multiple domains
- **`/java/agents/`** - 2 Java-based agents with equivalent functionality
- **Multi-language support** for the same agent concepts

### Agent Categories

**Business Intelligence & Analytics:**
- `data-science/` - Multi-agent system for data analysis via NL2SQL and NL2Python
- `time-series-forecasting/` - BigQuery ML forecasting models
- `brand-search-optimization/` - E-commerce product enhancement

**Financial Services:**
- `financial-advisor/` - Educational financial content with specialized sub-agents
- `fomc-research/` - Market event analysis with workflow orchestration
- `auto-insurance-agent/` - Insurance management

**Customer Service & Support:**
- `customer-service/` - Home & garden support with session management
- `software-bug-assistant/` - IT bug resolution (Python + Java implementations)
- `travel-concierge/` - Travel planning with booking integration

**Content & Research:**
- `academic-research/` - Publication discovery with specialized search agents
- `RAG/` - Document-based Q&A using Vertex AI RAG Engine
- `llm-auditor/` - Content verification with critic/reviser pattern
- `gemini-fullstack/` - Advanced fullstack research with React frontend

### Agent Architecture Patterns

**Single Agent Pattern:**
- Direct tool integration with focused functionality
- Simple conversational flow, minimal routing logic
- Examples: `RAG` (Vertex AI RAG retrieval), `auto-insurance-agent`

**Multi-Agent Pattern:**
- Router agent coordinating specialized sub-agents in `sub_agents/` directories
- Division of labor with domain-specific expertise
- Examples: `data-science` (analytics/bigquery/bqml), `financial-advisor` (risk/trading/execution analysts)

**Workflow Pattern:**
- Sequential task execution with state management
- Human-in-the-loop capabilities and callback systems
- Examples: `fomc-research` (research→extract→summarize→analyze), `customer-service` (session tracking)

### Directory Structure

**Python Agent Structure:**
```
agent-name/
├── agent_name/                    # Core agent code (underscore naming)
│   ├── sub_agents/               # Sub-agent definitions
│   │   ├── agent_name/
│   │   │   ├── tools/           # Sub-agent specific tools
│   │   │   ├── agent.py         # Sub-agent logic
│   │   │   └── prompt.py        # Sub-agent prompts
│   ├── tools/                   # Main agent tools
│   ├── agent.py                 # Main agent logic
│   └── prompt.py                # Main agent prompts
├── deployment/                   # Deployment scripts
├── eval/                        # Evaluation data and scripts
├── tests/                       # Unit tests
├── .env.example                 # Environment template
├── pyproject.toml               # Python dependencies
└── README.md                    # Agent documentation
```

**Java Agent Structure:**
```
agent-name/
├── src/
│   ├── main/java/com/google/adk/samples/agent/
│   │   ├── Agent.java           # Core agent logic
│   │   ├── tools/               # Custom tools
│   │   ├── services/            # Business logic
│   │   └── Main.java            # Entry point
│   └── test/java/               # Unit tests
├── pom.xml                      # Maven configuration
└── README.md                    # Agent documentation
```

## Key Technologies

### Core Frameworks
- **Google ADK** - Primary agent framework (Python 1.3.0+, Java 0.1.0)
- **Vertex AI** - Google Cloud AI platform integration with Gemini models
- **MCP (Model Context Protocol)** - Tool definition standard for external integrations

### Data and Integration
- **BigQuery** - Data warehousing, ML models, and NL2SQL capabilities
- **Vertex AI RAG Engine** - Retrieval-augmented generation for document Q&A
- **PostgreSQL** - Relational database with vector extensions (some agents)

### Development Tools
- **Python**: uv/Poetry for dependencies, ruff/mypy/codespell for linting
- **Java**: Maven for build management, JDK 17+ required
- **Frontend**: React 19 + TypeScript + Vite (gemini-fullstack)

## Working with Agents

### Environment Setup
1. Copy `.env.example` to `.env` in the agent directory
2. Fill in required environment variables (API keys, project IDs)
3. Set up Google Cloud credentials for Vertex AI access

### Development Workflow
1. **Choose agent** from the 18 Python or 2 Java options
2. **Navigate** to `python/agents/<agent-name>` or `java/agents/<agent-name>`
3. **Read agent README** for specific setup instructions
4. **Install dependencies** using Poetry/uv (Python) or Maven (Java)
5. **Configure environment** variables and credentials
6. **Run agent** using `adk run .` or `adk web`
7. **Test** using pytest (Python) or `mvn test` (Java)
8. **Evaluate** using provided evaluation scripts

### Testing and Evaluation
- **Unit tests** in `tests/` directory test individual components
- **Evaluation scripts** in `eval/` directory test end-to-end agent performance
- **Test data** in `.test.json` and `.evalset.json` files
- **Configuration** in `test_config.json` files

### Deployment
- **Local deployment** via ADK CLI tools
- **Cloud deployment** to Vertex AI Agent Engine
- **Container deployment** via provided Dockerfiles
- **Scripts** in `deployment/` directory for automated deployment

## Important Notes

- **Python versions**: Minimum 3.9+ (newer agents prefer 3.11+)
- **Java version**: JDK 17+ required for all Java agents
- **Google Cloud**: Most agents require GCP project with Vertex AI API enabled
- **Naming convention**: Directory names use hyphens, Python modules use underscores
- **Dependencies**: Each agent has independent pyproject.toml/pom.xml - check agent-specific versions
- **Environment**: Copy `.env.example` to `.env` and configure before running agents
- **ADK versions**: Python agents use ADK 1.0.0-1.3.0, Java agents use 0.1.0