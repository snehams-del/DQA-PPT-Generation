# 💵💱💶 Currency Agent (TypeScript + ADK + MCP)

[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Framework](https://img.shields.io/badge/Framework-ADK-4285F4.svg)](https://github.com/google/adk-js)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A sample agent demonstrating ADK + MCP working together in TypeScript. It leverages Google's **Agent Development Kit (ADK) for TypeScript** ([`@google/adk`](https://github.com/google/adk-js)) to create a currency converter agent that can convert between different countries' currencies.

## Overview

The sample aims at laying out a foundation and showcasing the capabilities
of ADK + MCP in TypeScript. It is a currency converter agent that can convert between different
countries' currencies.

### <img height="20" width="20" src="../../../../python/agents/currency-agent/images/mcp-favicon.ico" alt="MCP Logo" /> Model Context Protocol (MCP)

> MCP is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect AI models to different data sources and tools. - [Anthropic](https://modelcontextprotocol.io/introduction)

The MCP server in this example exposes a tool `get_exchange_rate` that can be used to get the exchange rate between two currencies such as USD and EUR. It leverages the [Frankfurter](https://www.frankfurter.dev/) API to get the currency exchange rate. Our agent uses an MCP client to invoke this tool when needed.

**Note:** The MCP server is implemented in Python and should be run separately. See the [Python currency agent README](../../../../python/agents/currency-agent/README.md) for MCP server setup.

### <img height="20" width="20" src="../../../../python/agents/currency-agent/images/adk-favicon.ico" alt="ADK Logo" /> Agent Development Kit (ADK)

> ADK is a flexible and modular framework for developing and deploying AI agents. While optimized for Gemini and the Google ecosystem, ADK is model-agnostic, deployment-agnostic, and is built for compatibility with other frameworks. - [ADK](https://github.com/google/adk-js)

ADK for TypeScript is used as the orchestration framework for creating our currency agent in this sample. It handles the conversation with the user and invokes our MCP tool when needed.

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- TypeScript 5.3+
- Git, for cloning the repository

### Installation

1. Clone the repository:

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/typescript/agents/currency_agent
```

2. Install dependencies:

```bash
npm install
```

3. Configure environment variables (via `.env` file):

There are two different ways to call Gemini models:

- Calling the Gemini API directly using an API key created via Google AI Studio.
- Calling Gemini models through Vertex AI APIs on Google Cloud.

> [!TIP] 
> An API key from Google AI Studio is the quickest way to get started.
> 
> Existing Google Cloud users may want to use Vertex AI.

<details open>
<summary>Gemini API Key</summary> 

Get an API Key from Google AI Studio: https://aistudio.google.com/apikey

Create a `.env` file by running the following (replace `<your_api_key_here>` with your API key):

```sh
echo "GOOGLE_API_KEY=<your_api_key_here>" >> .env
echo "GOOGLE_GENAI_USE_VERTEXAI=FALSE" >> .env
```

</details>

<details>
<summary>Vertex AI</summary>

To use Vertex AI, you will need to [create a Google Cloud project](https://developers.google.com/workspace/guides/create-project) and [enable Vertex AI](https://cloud.google.com/vertex-ai/docs/start/cloud-environment).

Authenticate and enable Vertex AI API:

```bash
gcloud auth login
# Replace <your_project_id> with your project ID
gcloud config set project <your_project_id>
gcloud services enable aiplatform.googleapis.com
```

Create a `.env` file by running the following (replace `<your_project_id>` with your project ID):
```sh
echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> .env
echo "GOOGLE_CLOUD_PROJECT=<your_project_id>" >> .env
echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
```

</details>

4. Configure MCP Server URL (optional):

By default, the agent connects to `http://localhost:8080/mcp`. If your MCP server runs on a different URL, add it to your `.env` file:

```sh
echo "MCP_SERVER_URL=http://localhost:8080/mcp" >> .env
```

Now you are ready for the fun to begin!

## Local Deployment

### MCP Server

First, start the MCP Server. The MCP server is implemented in Python. Navigate to the Python currency agent directory and start it:

```bash
cd ../../../../python/agents/currency-agent
uv run mcp-server/server.py
```

The MCP server will start on port 8080.

### TypeScript Agent

In a separate terminal, navigate back to the TypeScript agent directory and run the agent:

```bash
cd typescript/agents/currency_agent
npm run build
npm start
```

Or for development with auto-reload:

```bash
npm run dev
```

## Usage

### Running the Test Client

The easiest way to test the agent is using the provided test client:

```bash
npm run test
```

This will run several test scenarios:
- Single-turn conversation (e.g., "How much is 100 USD in CAD?")
- Multi-turn conversation (e.g., "How much is 100 USD?" followed by "in GBP")
- Off-topic test (to verify the agent stays focused on currency conversions)

### Programmatic Usage

The agent can also be used programmatically by importing and using the `rootAgent`:

```typescript
import { rootAgent } from './currency_agent/agent';
import { InMemoryRunner } from '@google/adk';

// Create a runner
const runner = new InMemoryRunner(rootAgent);

// Run a conversation
const response = await runner.run({
  messages: [{
    role: 'user',
    parts: [{ text: 'How much is 100 USD in EUR?' }]
  }]
});

console.log(response);
```

### Example: Using the Test Client Programmatically

You can also import and use the test functions:

```typescript
import { runSingleTurnTest, runMultiTurnTest } from './currency_agent/test_client';
import { InMemoryRunner } from '@google/adk';
import { rootAgent } from './currency_agent/agent';

const runner = new InMemoryRunner(rootAgent);
await runSingleTurnTest(runner);
await runMultiTurnTest(runner);
```

## Project Structure

```
currency_agent/
├── currency_agent/
│   ├── agent.ts          # Main agent definition
│   ├── config.ts         # Configuration and environment variables
│   ├── test_client.ts     # Test client demonstrating usage
│   └── tools/
│       └── mcp_tool.ts   # MCP tool integration
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE file](../../../../LICENSE) for details.
