# Status Messenger Sample

This sample demonstrates how to use the `status_messenger` tool in the Google Agent Development Kit (ADK) to send real-time status updates to a client application. It features a web-based chat interface built with FastAPI and WebSockets.

## Overview

The application consists of a multi-agent system that simulates a research assistant. When a user submits a query, the agents work together to research the topic, providing status updates to the user along the way. This showcases how to keep users informed during long-running processes.

### Key Components

*   **`main.py`**: A FastAPI application that serves the web interface and handles WebSocket connections. It manages the agent sessions and broadcasts status messages received from the `status_messenger` tool to the client.
*   **`example_agent/agent.py`**: Defines the agent logic. It includes a `root_agent` that coordinates the workflow, a `reasoning_agent` that performs research, and a `search_agent` that uses the `google_search` tool. The `root_agent` and `reasoning_agent` use the `status_message` tool to send updates.
*   **`static/index.html`**: The frontend of the application, providing a simple chat interface for users to interact with the agent.
*   **`requirements.txt`**: A list of the Python dependencies required to run the sample.

## Setup and Installation

1.  **Install Dependencies:**
    Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```


## How to Run

1.  **Start the Application:**
    Run the following command:
    ```bash
    ./run_app.sh
    ```
    This will start the FastAPI server.

2.  **Open the Web Interface:**
    Open your web browser and navigate to `http://127.0.0.1:8000`. You should see the chat interface.

3.  **Interact with the Agent:**
    Type a research query into the chat box and press Enter. You will see status messages from the agent as it processes your request, followed by the final answer.

## How it Works

1.  The user connects to the web application, which establishes a WebSocket connection with the FastAPI server.
2.  When the user sends a message, it is passed to the `root_agent`.
3.  The `root_agent` and its sub-agents (`reasoning_agent` and `search_agent`) process the request.
4.  Throughout the process, the agents call the `status_message` tool to send updates.
5.  The `status_messenger` tool adds these messages to a queue.
6.  A background task in `main.py` reads from the queue and broadcasts the status messages to the appropriate client via the WebSocket.
7.  The final result from the agent is also sent to the client.
