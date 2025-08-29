# Agent-Agnostic Safety Plugins
## Overview
This repository provides an example of a multi-agent system built with the Agent Development Kit (ADK), focusing on how to implement global safety guardrails using ADK's plugin feature. The system includes two distinct safety plugins: one that uses an agent as a judge and another that leverages the Model Armor API.

## Safety Plugins
The core of this example is demonstrating safety plugins using two different approaches: Gemini as a judge and Model Armor. Both plugins use hooks to send relevant messages and content to their respective safety filters, which then determine whether the content should be filtered or blocked.

Another key goal of these plugins is to prevent session poisoning by not saving harmful content to session memory, even if the initial LLM response correctly identified it as malicious. This is crucial because a class of safety vulnerabilities can exploit existing harmful messages in the session to elicit further unsafe responses from agents.

Both plugins operate on the following hooks:

* `on_user_message_callback`: Sends the user's message to the safety classifier. If the message is deemed unsafe, it is replaced with a message indicating that it was removed. The plugin then responds with a canned message.
* `before_tool_callback`: Sends the tool name and inputs to the safety classifier. If unsafe, the tool call is blocked and returns an error as if the tool itself had failed due to a safety violation.
* `after_tool_callback`: Sends the tool's output to the safety classifier. Performs the same action as `before_tool_callback`
* `after_model_callback`: Sends the model's response to the safety classifier. If the response is detected as unsafe, it is replaced with a canned message stating that the model's response was removed.

The plugins are attached to the `Runner` in `main.py`, which is the ADK's main orchestrator, providing guardrails for all agents using the runner (i.e. the `root_agent` and `sub_agent`).

### Gemini as a Judge Plugin ⚖️
The `LlmAsAJudge` plugin uses a large language model (LLM), specifically Gemini 2.5 Flash Lite, to function as a safety filter. The LLM agent itself acts as the safety classifier.

**Configuration**

The `LlmAsAJudge` class can be configured via its constructor:

* `judge_agent`: You can specify which LLM agent to use as the judge. The default is `default_jailbreak_safety_agent`, which is an agent designed to respond with only "SAFE" or "UNSAFE," but you can swap it out with any other agent instance.

* `judge_on`: This set determines which callbacks will trigger the judge. By default, it's set to check the `USER_MESSAGE` and `TOOL_OUTPUT`, but you can add or remove checks for `BEFORE_TOOL_CALL` and `MODEL_OUTPUT`.

* `analysis_parser`: This is a function that parses the text output from the judge agent into a boolean value (True for unsafe, False for safe). By default, it checks if the string "UNSAFE" is present in the judge's response. You can implement your own parser to handle different judge outputs, allowing for custom safety logic.

### Model Armor Plugin 🛡️
The `ModelArmorSafetyFilterPlugin` integrates safety with the [Model Armor API](https://cloud.google.com/security-command-center/docs/model-armor-overview). This plugin performs content safety checks by sending user prompts and model responses to the Model Armor service.

If the API identifies any content violations based on the configured Model Armor template, it modifies the agent's flow, returning a predetermined message to the user, similar to the LLM judge plugin.

*Note*: To use this plugin, you must have a Model Armor template in a Google Cloud Platform (GCP) project. Please refer to the [official documentation on how to create a template](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates). Once you have created a template, you will need to modify the plugin's constructor parameters with your project ID, location ID, and template ID to proceed.

## Setup and Installation

1.  **Prerequisites**

    *   Python 3.11+
    *   Poetry
        *   For dependency management and packaging. Please follow the
            instructions on the official
            [Poetry website](https://python-poetry.org/docs/) for installation.

        ```bash
        pip install poetry
        ```

    * A project on Google Cloud Platform
    * Google Cloud CLI
        *   For installation, please follow the instruction on the official
            [Google Cloud website](https://cloud.google.com/sdk/docs/install).

2.  **Installation**

    ```bash
    # Clone this repository.
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/safety-plugins
    # Install the package and dependencies.
    # Note for Linux users: If you get an error related to `keyring` during the installation, you can disable it by running the following command:
    # poetry config keyring.enabled false
    # This is a one-time setup.
    poetry install
    ```

3.  **Configuration**

    *   Set up Google Cloud credentials.

        *   You may set the following environment variables in your shell, or in
            a `.env` file instead.

        ```bash
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT=<your-project-id>
        export GOOGLE_CLOUD_LOCATION=<your-project-location>
        export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>  # Only required for deployment on Agent Engine
        ```

    *   Authenticate your GCloud account.

        ```bash
        gcloud auth application-default login
        gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
        ```
	* Please edit the environment variables in `main.py`.
      ```python
      os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
      os.environ["GOOGLE_CLOUD_PROJECT"] = "YOUR_PROJECT_ID_HERE"
      os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
      os.environ["GOOGLE_API_KEY"] = "YOUR_VALUE_HERE"
      os.environ["MODEL_ARMOR_TEMPLATE_ID"] = "YOUR_TEMPLATE_ID_HERE"
      ```

## Running the Agent

**To use the plugins, please comment the code in `main.py`**
```python
 runner = InMemoryRunner(
    agent=root_agent,
    app_name=APP_NAME,
    plugins=[
        # LlmAsAJudge(),
        # ModelArmorSafetyFilter(
        #     project_id="YOUR_PROJECT_ID_HERE",
        #     location_id="us-central1",
        #     template_id="YOUR_TEMPLATE_ID_HERE",
        # ),
    ],
    )
```

Navigate to the agent's directory and run the main file as a python module with
```bash
# Navigate to correct directory.
cd adk-samples/python/agents/safety-plugins
# Run the agent as a module.
python3 -m safety_plugins.main
```

Additionally, navigate to the `tools.py` file and add additional text to the tool output that the plugins will be able to filter. You can add benign, but nonsensical, text that mimics a potential prompt injection or an undesirable output. This will allow you to see the plugins in action across the different agents and their various outputs.
