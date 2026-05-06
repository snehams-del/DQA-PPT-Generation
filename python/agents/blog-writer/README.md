# Blogger Agent

This sample contains a multi-agent technical writing assistant built with the Google Agent Development Kit (ADK).

## Overview

The orchestrator coordinates four specialist sub-agents to help users go from idea to final publication:

- Plan a technical outline.
- Write a complete first draft.
- Iteratively edit based on feedback.
- Generate social media copy.

## Quick Start With Agent Starter Pack (Recommended)

The fastest way to create a production-ready project from this sample is:

```bash
uvx agent-starter-pack create my-blog-writer -a adk@blogger-agent
cd my-blog-writer
```

The starter pack scaffolds CI/CD, deployment options, and other production assets.

## Local Development (This Repository)

### 1. Install Dependencies

```bash
uv sync --group dev
```

### 2. Configure Environment

Create a `.env` file in this directory and set at least:

```bash
GOOGLE_CLOUD_PROJECT=<your-project-id>
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=True
```

### 3. Authenticate

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```

### 4. Run the Agent

CLI:

```bash
uv run adk run blogger_agent
```

Web UI:

```bash
uv run adk web
```

## Tests, Lint, and Type Checks

Run from this folder:

```bash
uv run pytest -s -W default
uv run ruff check . --fix
uv run ruff format .
uv run mypy .
```

## Project Layout

- `blogger_agent/`: main package and agent definitions.
- `blogger_agent/sub_agents/`: planner, writer, editor, and social agents.
- `eval/`: evaluation datasets and evaluation tests.
- `tests/`: integration and smoke tests.
