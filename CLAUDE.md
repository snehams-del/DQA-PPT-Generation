# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python Development (using Poetry or uv)

**Package Management:**
```bash
# Poetry
poetry install
poetry run <command>

# uv (preferred for newer agents)
uv sync
uv run <command>
```

**Running Agents:**
```bash
# CLI mode (from agent directory)
adk run .

# Web UI mode (from agent directory)
adk web

# API server mode (for fullstack agents)
adk api_server app --allow_origins="*"
```

**Linting and Formatting:**
```bash
# Modern Python (ruff + mypy + codespell)
ruff check . --diff
ruff format . --check --diff
mypy .
codespell

# Legacy tools (some agents)
black .
pyink .
pylint .
flake8 .
```

**Testing:**
```bash
# Run tests
pytest
pytest -vv -s
pytest --cov

# Run specific test file
pytest tests/test_agents.py
```

**Evaluation:**
```bash
# Run agent evaluation
adk eval <agent_name> eval/data/eval_data.evalset.json --config_file_path eval/data/test_config.json
```

### Java Development (using Maven)

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
# Execute main class
mvn exec:java

# ADK Dev UI
mvn compile exec:java -Dexec.args="--server.port=8080"
```

### Fullstack Development (gemini-fullstack)

**Using Makefile:**
```bash
make install        # Install all dependencies
make dev           # Run both frontend and backend
make dev-backend   # Run backend only
make dev-frontend  # Run frontend only
make lint          # Run all linting
```

## Repository Architecture

### High-Level Structure

This repository contains **Agent Development Kit (ADK) samples** demonstrating various AI agent patterns:

- **`/python/agents/`** - 18 Python-based agents across multiple domains
- **`/java/agents/`** - 2 Java-based agents with equivalent functionality
- **Multi-language support** for the same agent concepts

### Agent Categories

**Business Intelligence & Analytics:**
- `data-science/` - Multi-agent system for data analysis
- `time-series-forecasting/` - BigQuery ML forecasting
- `brand-search-optimization/` - E-commerce product enhancement

**Financial Services:**
- `financial-advisor/` - Educational financial content
- `fomc-research/` - Market event analysis
- `auto-insurance-agent/` - Insurance management

**Customer Service & Support:**
- `customer-service/` - Home & garden support
- `software-bug-assistant/` - IT bug resolution
- `travel-concierge/` - Travel planning

**Content & Research:**
- `academic-research/` - Publication discovery
- `RAG/` - Document-based Q&A
- `llm-auditor/` - Content verification
- `gemini-fullstack/` - Advanced fullstack research

### Agent Architecture Patterns

**Single Agent Pattern:**
- Direct tool integration
- Simple conversational flow
- Examples: `personalized-shopping`, `RAG`

**Multi-Agent Pattern:**
- Router agent with specialized sub-agents
- Hierarchical structures with division of labor
- Examples: `data-science`, `financial-advisor`, `marketing-agency`

**Workflow Pattern:**
- Sequential task execution
- Human-in-the-loop capabilities
- Examples: `gemini-fullstack`, `fomc-research`

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
- **Google ADK** - Primary agent framework (Python 1.0.0+, Java 0.1.0)
- **Vertex AI** - Google Cloud AI platform integration
- **Gemini Models** - LLM integration via Vertex AI

### Data and Integration
- **BigQuery** - Data warehousing and ML
- **PostgreSQL** - Relational database with vector extensions
- **MCP (Model Context Protocol)** - Tool definition standard

### Development Tools
- **Python**: Poetry/uv for dependencies, ruff/mypy for linting
- **Java**: Maven for build management, JUnit for testing
- **Frontend**: React 19 + TypeScript + Vite (fullstack examples)

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

- **Python versions**: 3.10-3.13 supported (varies by agent)
- **Java version**: JDK 17+ required
- **Google Cloud**: Most agents require GCP project and Vertex AI access
- **Naming convention**: Directory names use hyphens, Python modules use underscores
- **Dependencies**: Each agent has its own pyproject.toml/pom.xml configuration
- **Environment**: `.env` files are required but not committed (use `.env.example`)