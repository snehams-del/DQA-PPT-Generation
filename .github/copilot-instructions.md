# Copilot Instructions for AI Coding Agents

This repository contains sample agent projects for the Agent Development Kit (ADK) in both Python and Java. Follow these guidelines to be immediately productive as an AI coding agent in this codebase.

## Architecture Overview
- Each agent is organized in its own directory (e.g., `python/agents/agent-name/` or `java/agents/agent-name/`).
- Agents typically consist of:
  - Main agent logic (`agent.py` for Python, `Agent.java` for Java)
  - Tool functions (Python: functions in agent module; Java: methods/classes)
  - Configuration files (`.env`, `pyproject.toml`, `pom.xml`)
  - Deployment scripts and documentation (`README.md`, `deployment/`)
- Agents interact with external LLMs (Gemini, Vertex AI) via API keys in `.env` or environment variables.

## Developer Workflows
- **Python Agents:**
  - Create and activate a virtual environment: `python -m venv .venv && source .venv/bin/activate`
  - Install dependencies: `pip install -r requirements.txt` or `pip install google-adk`
  - Run agent locally: `adk web` (for Dev UI) or `adk run` (terminal)
  - API keys go in `.env` (see agent README for details)
- **Java Agents:**
  - Use Java 17+
  - Build with Maven: `mvn clean install`
  - Run agent: `adk web` or `adk run` (after build)
  - Set environment variables for API keys

## Project-Specific Patterns
- Agents are defined with a root agent object (Python: `root_agent = Agent(...)`).
- Tool functions are explicitly listed in the agent's `tools` array.
- Model selection and authentication are controlled via `.env` or environment variables.
- Each agent's README documents its tools, configuration, and usage.
- Example prompts for agent testing are provided in README files.

## Integration Points
- Agents communicate with LLMs using the ADK library (`google-adk` for Python).
- External dependencies are managed via `requirements.txt`, `pyproject.toml`, or `pom.xml`.
- Deployment and cloud integration scripts are found in `deployment/` directories.
- For Vertex AI, authentication uses `gcloud auth application-default login`.

## Conventions & Patterns
- Place all agent code in its own directory under `python/agents/` or `java/agents/`.
- Use `.env` for secrets and configuration (never commit actual API keys).
- Document agent capabilities, tools, and example prompts in each agent's README.
- Follow the ADK quickstart for new agent setup: https://google.github.io/adk-docs/get-started/quickstart/#create-agent-project

## Key Files & Directories
- `python/agents/*/agent.py` – Main agent logic
- `python/agents/*/.env` – API keys and config
- `python/agents/*/README.md` – Agent documentation
- `java/agents/*/Agent.java` – Main agent logic
- `java/agents/*/pom.xml` – Java dependencies
- `deployment/` – Deployment scripts and configs

## Example: Minimal Python Agent Structure
```
multi_tool_agent/
    __init__.py
    agent.py
    .env
    README.md
```

## Troubleshooting
- If an agent does not appear in the Dev UI, ensure you are running `adk web` from the parent directory of the agent folder.
- For authentication issues, verify `.env` or environment variables are set correctly.

---
For more details, see the ADK documentation: https://google.github.io/adk-docs/
