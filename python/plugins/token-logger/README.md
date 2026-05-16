# Token Logger Plugin

This plugin logs token usage for LLM requests, helping to monitor and optimize token consumption.

## Installation
```bash
poetry install
```

## Usage

Once installed, you can use the plugin in your agent by importing it in the InMemoryRunner.

```python
from token_logger import TokenCounterLoggerPlugin

async def main():
  runner = InMemoryRunner(
      agent=your_agent,
      # Add your plugin here. You can add multiple plugins.
      plugins=[TokenCounterLoggerPlugin()],
  )
```

## Example
You can find a simple example of how to use this plugin in the `example.py` file.

```bash
poetry run python example.py
```
