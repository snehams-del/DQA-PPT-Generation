# Agent Development Kit (ADK) JavaScript/TypeScript Samples

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

<img src="https://github.com/google/adk-docs/blob/main/docs/assets/agent-development-kit.png" alt="Agent Development Kit Logo" width="150">

This collection provides ready-to-use sample agents built on top of JavaScript/TypeScript
[Agent Development Kit](https://github.com/google/adk-typescript). These agents
cover a range of common use cases and complexities, from simple conversational
bots to complex multi-agent workflows.

## 🚀 Getting Started with JavaScript/TypeScript Samples

Follow these steps to set up and run the sample agents:

1.  **Prerequisites:**
    *   **Install ADK for TypeScript:** Ensure you have the Agent
        Development Kit for TypeScript installed and configured. Follow the JavaScript/TypeScript instructions in the
        [ADK Installation Guide](https://google.github.io/adk-docs/get-started/installation/#typescript).
    *   **Node.js or Bun:** You'll need either Node.js 18+ or [Bun](https://bun.sh) 1.0+ installed.
        Bun is recommended for faster execution and native TypeScript support.
    *   **Set Up Environment Variables:** Each agent example relies on a `.env`
        file for configuration (like API keys, Google Cloud project IDs, and
        location). This keeps secrets out of the code.
        *   You will need to create a `.env` file in each agent's directory you
            wish to run (usually by copying the provided `.env.example`).
        *   Setting up these variables, especially obtaining Google Cloud
            credentials, requires careful steps. Refer to the **Environment
            Setup** section in the [ADK Installation
            Guide](https://google.github.io/adk-docs/get-started/installation/#typescript)
            for detailed instructions.
    *   **Google Cloud Project (Recommended):** While some agents might run
        locally with just an API key, most leverage Google Cloud services like
        Vertex AI and BigQuery. A configured Google Cloud project is highly
        recommended. See the
        [ADK Quickstart](https://google.github.io/adk-docs/get-started/typescript)
        for setup details.


2.  **Clone this repository:**

    To start working with the ADK JavaScript/TypeScript samples, first clone the public `adk-samples` repository:
    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/js
    ```

3.  **Explore the Agents:**

    *   Navigate to the `agents/` directory.
    *   The `agents/README.md` provides an overview and categorization of the available agents.
    *   Browse the subdirectories. Each contains a specific sample agent with its own
    `README.md`.

4.  **Run an Agent:**
    *   Choose an agent from the `agents/` directory.
    *   Navigate into that agent's specific directory (e.g., `cd agents/image-approval-agent`).
    *   Follow the instructions in *that agent's* `README.md` file for specific
        setup (like installing dependencies via `bun install` or `npm install`) and running
        the agent.
    *   Browse the folders in this repository. Each agent and tool have its own
        `README.md` file with detailed instructions.

**Notes:**

These agents have been built and tested using
[Google models](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)
on Vertex AI. You can test these samples with other models as well. Please refer
to [ADK Tutorials](https://google.github.io/adk-docs/tutorials/) to use
other models for these samples.

## 🧱 Repository Structure
```bash
.
├── js                      # Contains all the JavaScript/TypeScript sample code
│   ├── agents                  # Contains individual agent samples
│   │   ├── agent1              # Specific agent directory
│   │   │   └── README.md       # Agent-specific instructions
│   │   ├── agent2
│   │   │   └── README.md
│   │   ├── ...
│   └── README.md               # This file (Repository overview)
```
