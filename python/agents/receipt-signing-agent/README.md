# Receipt-Signing Agent - Cryptographic Audit Trail for ADK

**Created by [Tom Farley](https://github.com/tomjwxf)**

A research agent that produces Ed25519-signed cryptographic receipts for every tool call. Receipts follow the [IETF Internet-Draft](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/) format and are independently verifiable offline.

## Why

When ADK agents run in production, compliance teams need verifiable proof of what happened. Centralized logs can be tampered with. This agent produces a signed receipt chain where:

- Every tool call is Ed25519-signed (tamper-evident)
- Tool inputs/outputs are SHA-256 hashed (privacy-preserving)
- Receipts are chain-linked via previousReceiptHash (ordering is tamper-evident)
- Anyone can verify offline without trusting the agent operator

## Project Structure

```
receipt-signing-agent/
├── README.md
├── pyproject.toml
├── receipt_agent/
│   ├── __init__.py
│   ├── agent.py          # Agent definition with ReceiptPlugin
│   └── tools.py          # Example research tools
└── tests/
    └── test_receipts.py  # Verify receipt chain integrity
```

## Setup

```bash
# Install dependencies
pip install google-adk protect-mcp-adk

# Set your Gemini API key
export GOOGLE_API_KEY=your-key-here
```

## Run

```bash
# Run with ADK dev server
cd receipt-signing-agent
adk web
```

Or programmatically:

```python
from receipt_agent.agent import agent, receipt_plugin

# After agent runs, check receipts
print(f"Receipts signed: {receipt_plugin.receipt_count}")
receipt_plugin.export_receipts("receipts.jsonl")
print(f"Verify: {receipt_plugin.get_verification_command()}")
```

## Verify Receipts

After the agent runs, verify the entire receipt chain:

```bash
npx @veritasacta/verify@0.2.5 receipts.jsonl --key <public-key-hex>
# Exit 0 = all valid, 1 = tampered, 2 = malformed
```

## How It Works

The agent uses the `ReceiptPlugin` from [protect-mcp-adk](https://pypi.org/project/protect-mcp-adk/), which hooks into ADK's `BasePlugin` interface:

1. `after_tool_callback` fires after every tool execution
2. The plugin signs `JCS(payload)` with Ed25519 (RFC 8032 + RFC 8785)
3. Each receipt links to the previous via `previousReceiptHash`
4. Receipts are exported as JSONL for offline verification

## Receipt Format

```json
{
  "payload": {
    "type": "protectmcp:decision",
    "spec": "draft-farley-acta-signed-receipts-01",
    "tool_name": "web_search",
    "tool_input_hash": "sha256:ff7e27...",
    "decision": "allow",
    "output_hash": "sha256:a3f8c9...",
    "session_id": "sess_a1b2c3",
    "sequence": 1,
    "previousReceiptHash": null
  },
  "signature": {
    "alg": "EdDSA",
    "kid": "sb:adk:de073ae6",
    "sig": "3da316..."
  }
}
```

## Interoperability

Receipts produced by this agent verify against the same tooling used by:
- [protect-mcp](https://npmjs.com/package/protect-mcp) (TypeScript, MCP/Claude Code)
- [Agent Passport System](https://github.com/aeoess/agent-passport-system) (TypeScript)

Four independent implementations produce interoperable receipts following the same IETF draft.

## Links

- [protect-mcp-adk on PyPI](https://pypi.org/project/protect-mcp-adk/)
- [IETF Draft: Signed Receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)
- [Verifier](https://npmjs.com/package/@veritasacta/verify) (Apache-2.0, offline)
- [Veritas Acta Protocol](https://veritasacta.com)
