## No Code MCP Agent for any MCP server (Runs on Agentspace and Cloud Run).

This is a prebuilt agent with the following features to operationalize your MCP servers within minutes and with security, access control and other features - 

1. Connect to any MCP server running behind IAM authentication.
2. Run the agent locally (for testing)
3. Deploy the agent on [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) and Register and use on [Google Agentspace](https://cloud.google.com/products/agentspace).
4. Deploy and run the agent on [Cloud Run](https://cloud.google.com/run) alongside your MCP Server

### Introduction
MCP servers on their own cannot be used without an agent. 

The customers have two options

1. Use desktop agent applications, IDE plugins (Cline, Claude Desktop)
2. Develop, deploy and secure agents Developed with Agent Development Frameworks like [Google's ADK](https://google.github.io/adk-docs/), Langchain, crew.ai etc.

For most (enterprise) customers - Handing out credentials (in order to run the MCP servers via agents using option 1) to individual desktop based users is not practical and poses a huge security risk.

That leaves them with option 2. But that has various barriers to entry

1. Developing an agent to talk to the MCP server
2. Deploying the agent
3. Managing and securing access
4. Managing performance, reliability and costs

This burdens the customers or their customers with lot of heavy lifting. And their MCP servers are either not used by their customers (creating a big feature gap against the compitition) or the MCP servers are used insecurely (option 1)

This No Code MCP Agent solves that!

### No Code MCP Agent

#### TL;DR

With No Code MCP Agent - 

1. Customer deploy their MCP server on cloud run
2. Protect the access with IAM Authentication
3. Clone this repository, install dependencies and
    1. Run `./adk_agent_operations.sh local_run` - To Test a prebuilt agent locally
    2. Run `./adk_agent_operations.sh agent_engine_deploy` - To deploy on Agent Engine
    3. Run `./adk_agent_operations.sh agentspace_register` - To register the agent in Agentspace
    4. (Optionally) with `./adk_agent_operations.sh cloudrun_deploy` They can also deploy this agent on Cloud Run alongside their MCP server in case Agentspace is not part of their deployment roadmap.

And that's it!

They can start using their MCP server as a tool from Agentspace.

### Detailed Instructions

#### Prerequsites

1. Your MCP server should be running with Streamable HTTP transport in Cloud run (We have provided a sample MCP server in case your MCP server is not ready yet).
2. Make sure that it is protected with IAM authentication
3. Clone this repository and install dependencies


```bash
# After cloning this repository
cd python/agents/mcp-iam-authn-agent

# if using uv 
uv sync
. .venv/bin/activate

# OR

# if using pip
python3 -m venv .venv
pip install -r mcp_agent/requirements.txt
. .venv/bin/activate

```
4. Create Environment file needed for subsequent operations.

    Go ahead and run the script that creates the environment file.

```bash
./adk_agent_operations.sh 

# Sample Output
INFO: No operation mode provided and './mcp_agent/.env' is not found.
INFO: Attempting to copy template 'aaa.conf' to './mcp_agent/.env'.
SUCCESS: 'aaa.conf' copied to './mcp_agent/.env'.
ACTION REQUIRED: Please update the variables in './mcp_agent/.env' before running this script with an operation mode.
```

🪧 **Optional (Testing with a Sample MCP Server):** 

If you just want to test using a sample MCP server that comes with this repository, you can use the following instructions


```bash

cd sample_mcp_server/
gcloud run deploy weather-mcp-service --region us-central1  --source .

# Say N on allow unauthenticated invocations question.

```

Create a service account and download the service account key for that account from IAM.

Then goto the deployed service and select it. Go to permissions (right hand top corner). Add the service account created earlier with "Cloud Run Invoker" role.


At this point you have

1. Repository set up
2. Either the sample MCP server or your actual MCP server running in Cloud Run behind IAM Authentication.
3. Make sure you have updated the environment variables in `SECTION - 1` in `mcp_agent/.env` file using your favorite editor.

#### Local run

🪧 **NOTE:**
> This is optional but recommended to so as to test the agent locally once.

Run the following command, in case you are missing the required environment variables, the script will prompt for you to update them (Check sample output 1). Else the agent should run locally (Check sample output 2).

```bash

./adk_agent_operations.sh local_run

```

<details>

<summary><b>Sample Output - 1 - Local run</b></summary>

```bash
INFO: Operation mode selected: 'local_run'.
--- Loading environment variables from './mcp_agent/.env' ---
--- Environment variables loaded. ---
--- Validating required environment variables for 'local_run' mode ---
INFO: Variable 'GOOGLE_GENAI_USE_VERTEXAI' is set and valid.
ERROR: Required environment variable 'GOOGLE_API_KEY' has an invalid value: 'NOT_SET'.
INFO: Variable 'GEMINI_MODEL' is set and valid.
INFO: Variable 'AGENT_NAME' is set and valid.
INFO: Variable 'AGENT_DESCRIPTION' is set and valid.
ERROR: Required environment variable 'MCP_AUDIENCE' has an invalid value: 'NOT_SET'.
INFO: Variable 'AGENT_PROMPT' is set and valid.
INFO: Variable 'MCP_TOOLSET_NAME' is set and valid.
ERROR: Required environment variable 'GOOGLE_APPLICATION_CREDENTIALS' has an invalid value: 'NOT_SET'.
--- Validation FAILED. Please check your './mcp_agent/.env' file. ---
```
</details>

<details>

<summary><b>Sample Output - 2 - Local run</b></summary>

```bash
INFO: Operation mode selected: 'local_run'.
--- Loading environment variables from './mcp_agent/.env' ---
--- Environment variables loaded. ---
--- Validating required environment variables for 'local_run' mode ---
INFO: Variable 'GOOGLE_GENAI_USE_VERTEXAI' is set and valid.
INFO: Variable 'GOOGLE_API_KEY' is set and valid.
INFO: Variable 'GEMINI_MODEL' is set and valid.
INFO: Variable 'AGENT_NAME' is set and valid.
INFO: Variable 'AGENT_DESCRIPTION' is set and valid.
INFO: Variable 'MCP_AUDIENCE' is set and valid.
INFO: Variable 'AGENT_PROMPT' is set and valid.
INFO: Variable 'MCP_TOOLSET_NAME' is set and valid.
INFO: Variable 'GOOGLE_APPLICATION_CREDENTIALS' is set and valid.
--- All required environment variables are VALID. ---
.
.
.
.
2025-09-09 17:07:20,798 - DEBUG - selector_events.py:64 - Using selector: EpollSelector
INFO:     Started server process [3926261]
INFO:     Waiting for application startup.

+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://127.0.0.1:8000.                         |
+-----------------------------------------------------------------------------+

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

```
</details>

Now test your agent locally on https://localhost:8000


#### Agent engine deployment and Agentspace registration


1. Create a Global Agentspace application and note down the application name.
2. Make sure you provide the Agentengine service account "Cloud Run Invoker" access on the MCP server Cloud Run service

🪧 **TIPS:**
1. You will have to update the environment variables in `SECTION - 2` and `SECTION - 3` in the `mcp_agent/.env` suggested by the script run.
2. Agent Engine Deployment generally takes a few minutes.

Run the following commands

```bash

# Agent Engine Deployment
./adk_agent_operations.sh agent_engine_deploy

# Agentspace registration
./adk_agent_operations.sh agentspace_register

```

Access your Agentspace application, Go to Integration, Copy and open "The link to your web app", open in new tab and goto Agents and access your agent.


#### Running the prebuilt agent in Cloud Run (For Non Agentspace customers).

If Agentspace is not where you / your customers want the agent to run, they can also run the Agent alongside the MCP server in Cloud Run itself.

> You may have to update the environment variables suggested by the script run.

```bash
# Running Agent in Cloud run (Alongside your MCP server)
./adk_agent_operations.sh cloudrun_deploy

# Say N on allow unauthenticated invocations question.

```

And then you can access the Agent on the Cloud Run Service URL.

**Accessing the authenticated agent**

1. Provide `Cloud Run Invoker` role to your users and ask them to run the following command (replace project id and region with the project id & region in which you have deployed the service)

```bash
gcloud run services proxy <name-of-ur-agent-service-on-cloudrun> --project PROJECT-ID --region YOUR-REGION
```

<details>

<summary><b>Sample Output Accessing Cloud Run service through local proxy</b></summary>


```bash
# You might be asked to install a component, for the proxy to work locally
This command requires the `cloud-run-proxy` component to be installed. Would
 you like to install the `cloud-run-proxy` component to continue command 
execution? (Y/n)?  Y

Proxying to Cloud Run service [agent-service] in project [project-xxx-yyy] region [us-central1]
http://127.0.0.1:8080 proxies to https://agent-service-abc1234-uc.a.run.app

```
</details>

### Additional features provided by the prebuilt agent
Not only does this agent provide no code operationalization of your MCP server, but also some nifty features.

1. Performance and LLM Cost optimizations - By controlling the value of environment variable `MAX_PREV_USER_INTERACTIONS` you can control how much historical context is sent to the LLM, thereby reducing LLM costs (as they are per token) and improving perfomance.
2. Wide compatibility with various MCP schema versions.


### Conclusion
🪧 **NOTE:**
[Google Cloud Marketplace](https://console.cloud.google.com/marketplace) can now list your MCP servers. You can fill [this form](https://docs.google.com/forms/d/e/1FAIpQLSesllyRR-HvLFZthYA8Cv4nQRUTOthHGgs-76DY9o2IntUL3A/viewform) and get started with listing your MCP server there. This provides discoverability to your MCP server to your Google Cloud Customers. And then they can operationlize your MCP server within minutes using the no code Agent provided here.

The prebuilt agent helps operationalize the MCP Server within minutes with only configuration changes. We have following the [following roadmap](#roadmap). Do let us know about your comments and watch this space for more updates.

#### Roadmap

1. End to end authentication (Agentspace to Agent Engine to MCP to Underlying application)
2. Accomodating multiple MCP servers