# Jailbreak safety plugin with Customer Service Agent.

### Setup
1. Use `venv` to create a virtual environment (e.g. `python -m venv my-agent-dev-env`)
2. Navigate to the `adk-samples/python/agents/customer-service` directory. 
3. Run the customer service agent as a module using `python -m customer_service.main`


### Usage

#### Flags
Use exactly exactly one of these flags:
* `--singleturn "prompt"`: Run the agent with a specified prompt for a single tun.
* `--multiturn`: Have a conversation with the agent (similar to `adk run`).
* `--eval`: Run the DeepTeam eval on this agent.

Optionally provide the `-s` or `--secure` flag to include the jailbreak plugin to filter for jailbreak prompts.

#### Examples
`python -m customer_service.main -s --singleturn "Hello, how are you?"`

`python -m customer_service.main --multiturn`

`python -m customer_service.main --secure --eval`

