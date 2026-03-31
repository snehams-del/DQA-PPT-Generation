# Frosty

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-ADK-4285F4.svg)](https://github.com/google/adk-python)
[![Snowflake](https://img.shields.io/badge/built%20for-Snowflake-29B5E8?logo=snowflake)](https://www.snowflake.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](../../../LICENSE)

Frosty is the original multi-agent Snowflake assistant implementation adapted
into the ADK samples repository with a thin wrapper package. The underlying
behavior is preserved by reusing Frosty's existing ADK root agent from
`src/frosty_ai/objagents/agent.py`.

## Overview

Frosty is a self-hosted agentic framework that turns plain-English requests
into Snowflake operations. It supports multiple model providers and includes a
large specialist-agent tree for data engineering, administration, governance,
security, inspection, and account monitoring.

This sample keeps the original implementation structure:

- `src/`: original Frosty source code
- `skills/`: original Frosty skill library
- `frosty/agent.py`: thin wrapper that exports Frosty's `root_agent` for ADK

## Agent Details

| Attribute | Detail |
|---|---|
| Interaction Type | Conversational |
| Complexity | Advanced |
| Agent Type | Multi Agent |
| Components | Root manager agent, lazy-loaded pillar agents, Snowflake tools, skills |
| Vertical | Data & Analytics / Snowflake |

## Project Structure

```text
frosty/
├── .env.example
├── README.md
├── pyproject.toml
├── frosty/
│   ├── __init__.py
│   └── agent.py
├── skills/
│   └── ...
├── src/
│   ├── session.py
│   ├── frosty_ai/
│   │   └── objagents/
│   │       ├── agent.py
│   │       ├── tools.py
│   │       ├── prompt.py
│   │       └── sub_agents/
│   │           └── ...
│   └── ...
└── tests/
    ├── conftest.py
    └── test_structure.py
```

## Setup

### Prerequisites

- Python 3.11+
- Snowflake access
- A supported model provider API key

### Installation

Clone the repository and move into the sample directory:

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/frosty
```

Then install dependencies:

```bash
uv sync
```

Copy `.env.example` to `.env` and fill in:

- Snowflake credentials
- application metadata
- one model provider configuration

## Run Locally

Start the ADK web UI from this directory:

```bash
uv run adk web
```

Or run the wrapped root agent directly:

```bash
uv run adk run frosty:root_agent --input "show me the top 10 customers by revenue"
```

## Environment Configuration

The included [.env.example](.env.example)
comes from the original Frosty project and supports:

- Snowflake username/password or authenticator flows
- Google, Anthropic, or OpenAI model providers
- optional OpenTelemetry exports
- optional Moltbook integration
- optional Frosty debug mode

## Notes On Exactness

This sample preserves the original Frosty implementation by vendoring the
project's `src/` and `skills/` directories directly into the sample. The ADK
sample package itself is only a thin wrapper so users can run the existing
Frosty `root_agent` through the standard ADK sample conventions.

## Verification

The included tests validate the sample structure and compile key Frosty entry
files:

```bash
pytest tests/test_structure.py
python3 -m compileall .
```

## Customization

If you want to keep this sample aligned with the upstream Frosty project, make
changes in the vendored `src/` and `skills/` trees rather than re-implementing
logic in the wrapper package.
