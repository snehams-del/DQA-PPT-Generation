# Blogger Agent Tests

This directory contains integration tests for the `blogger-agent`.

## How to Run

To run the test, first install dependencies from the project root:

```bash
uv sync --group dev
```

You can run the test from the root of the project using the following command:

```bash
uv run python -m tests.test_agent
```

## Test Scenario

The `test_agent.py` script is an integration test that runs the `blogger-agent` through a predefined sequence of user queries. This test is designed to simulate a typical conversation with the agent and ensure that it can handle the flow without errors.

The script will print the agent's responses to the console for each query in the sequence.
