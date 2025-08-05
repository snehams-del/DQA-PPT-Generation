# Model Garden Deploy Agent
##  Overview of the Agent

This project implements an ADK-based agent that provides a seamless, conversational interface for Google's Vertex AI Model Garden, a Google Cloud service for discovering, customizing, and deploying a variety of models from Google and Google Cloud partners.
Current methods of interacting with Model Garden, while powerful, are not very user-friendly, often requiring users to write code or navigate complex web console interfaces. This agent bridges that gap by allowing users to discover models, deploy them to an endpoint, and run inference on those models, using natural language prompts.

## Agent Details
### Features
The key features of the Model Garden Assistant include:

| Feature | Description |
| :--- | :--- |
| Interaction Type | Conversational |
| Complexity | Advanced |
| Agent Type | Multi Agent |
| Components | Tools, AgentTools |
| Vertical | LLMOps |

## Setup and Installation
### Prerequisites

* Python 3.11+
* Poetry
  * For dependency management and packaging. Please follow the instructions on the official Poetry website for installation.
```
pip install poetry
```
* A project on Google Cloud Platform
* Google Cloud CLI
  * For installation, please follow the instructions on the official [Google Cloud website.](https://cloud.google.com/sdk/docs/install)

## Installation
```
# Clone this repository.
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/model-garden-agent
# Install the package and dependencies.
poetry install
```
## Configuration
Set up Google Cloud credentials.
* You may set the following environment variables in your shell, or in a .env file instead.

```
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<your-project-id>
export GOOGLE_CLOUD_LOCATION=<your-project-location>
export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>  
# Only required for deployment on Agent Engine
```
* Authenticate your GCloud account.

```
gcloud auth application-default login
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```
## Running Agent
Using ```adk```
ADK provides convenient ways to bring up agents locally and interact with them. You may talk to the agent using the CLI:
```
adk run model_garden_agent
```
Or on a web interface:
```
adk web
```

The command adk web will start a web server on your machine and print the URL. You may open the URL, select "model_garden_agent" in the top-left drop-down menu, and a chatbot interface will appear on the right. The conversation is initially blank. Here are some example requests you may ask the Model Garden Agent to verify:
```
Who are you?
```
```
I am a helpful agent that assists users in deploying and managing AI models using Vertex AI Model Garden. I can help you with tasks like discovering models, getting setup recommendations, deploying models to endpoints, and running inference.
```
## Example Interaction

# Running Test/Eval
For running tests and evaluation, install the extra dependencies:
```
poetry install --with dev
```
Then the tests and evaluation can be run from the model_garden_agent directory using the pytest module:
```
python3 -m pytest tests
python3 -m pytest eval
```
```tests``` runs the agent on a sample request, and makes sure that every component is functional. ```eval``` is a demonstration of how to evaluate the agent, using the ```AgentEvaluator``` in ADK. It sends a couple requests to the agent and expects that the agent's responses match a pre-defined response reasonably well.

# Deployment
The Model Garden Agent can be deployed to Vertex AI Agent Engine using the following commands:
```
poetry install --with deployment
python3 deployment/deploy.py --create
```
When the deployment finishes, it will print a line like this:
```
Created remote agent: projects/<PROJECT_NUMBER>/locations/<PROJECT_LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>
```
If you forgot the AGENT_ENGINE_ID, you can list existing agents using:
```
python3 deployment/deploy.py --list
```
The output will be like:
```
All remote agents:

123456789 ("academic_research")
- Create time: 2025-05-10 09:33:46.188760+00:00
- Update time: 2025-05-10 09:34:32.763434+00:00
```
You may interact with the deployed agent using the ```test_deployment.py``` script
```
$ export USER_ID=<any string>
$ python3 deployment/test_deployment.py --resource_id=${AGENT_ENGINE_ID} --user_id=${USER_ID}
Found agent with resource ID: ...
Created session for user ID: ...
Type 'quit' to exit.
Input: Hello. What can you do for me?
Response: Hello! I'm an AI Research Assistant. I can help you analyze a seminal academic paper.

To get started, please provide the seminal paper you wish to analyze as a PDF.
```
To delete the deployed agent, you may run the following command:
```
python3 deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```