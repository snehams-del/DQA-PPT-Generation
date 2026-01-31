# Personal Assistant with Memory

An executive assistant for travel planning that remembers your preferences and plans itineraries accordingly using **Cognee** (Semantic memory system) and **Google ADK** (Agent framework).

## Overview

This example demonstrates how to build a personal assistant that:
- **Remembers** your travel preferences and dietary restrictions
- **Plans** personalized itineraries based on stored preferences
- **Searches** memory to retrieve relevant information when making recommendations
- **Adapts** recommendations based on your specific needs (e.g., vegetarian meals, hotel preferences, beach locations)

The assistant uses Cognee's Semantic Memory layer to store and retrieve user preferences, enabling context-aware travel planning.

## Architecture

- **Google ADK Framework**: [Agno](https://github.com/agno-agi/agno/) - For building intelligent agents
- **Memory Layer**: [Cognee](https://github.com/topoteretes/cognee/) - Semantic knowledge graph for persistent memory

We will directly use the integration provided by Cognee: [Google ADK <> Cognee](https://github.com/topoteretes/cognee-integration-google-adk)

## Prerequisites

- Python >= 3.10 and < 3.14
- [uv](https://github.com/astral-sh/uv) package manager
- API keys for your chosen LLM provider (i.e., Google)

## Installation

### 1. Create Virtual Environment

```bash
uv venv
source .venv/bin/activate
```

### 2. Install Dependencies

Uses Gemini (LLM) and [FastEmbed](https://github.com/qdrant/fastembed) (embeddings).

```bash
uv add cognee-integration-google-adk
```

## Configuration

Create a `.env` file in the project root with the appropriate environment variables. Similar to `.env.example`

```env
# For cognee operations

LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-2.5-flash
LLM_API_KEY=your-openai-api-key      
EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=jinaai/jina-embeddings-v2-base-en
EMBEDDING_DIMENSIONS=768

# For Agents- Gemini models (ADK execution)
GOOGLE_API_KEY=your-google-api-key    
```

## Usage

### Running the Default Stack (`app.py`)

```bash
cd travel_agent
uv run agent.py
```

The agent will:
1. Store your preferences in Cognee's memory
2. Demonstrate retrieval by planning a restaurant itinerary for Rome or any other place. 
3. Get personalized suggestion rather than generic responses. 

## How It Works

1. **Memory Storage**: When you provide preferences, the agent uses `add_tool` to store them in Cognee's semantic knowledge graph
2. **Memory Retrieval**: When planning itineraries, the agent uses `search_tool` to find relevant preferences
3. **Context-Aware Planning**: The agent applies retrieved preferences to generate personalized recommendations


## Troubleshooting

- **Import errors**: Ensure all dependencies are installed with `uv sync`
- **API key errors**: Verify your `.env` file contains valid API keys