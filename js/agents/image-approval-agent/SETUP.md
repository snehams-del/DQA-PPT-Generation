# Setup Guide

## Quick Start (5 minutes)

### 0. Install Bun (if you haven't already)

```bash
# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# Windows
powershell -c "irm bun.sh/install.ps1 | iex"

# Verify installation
bun --version
```

### 1. Install Dependencies

```bash
cd image-approval-agent
bun install
```

### 2. Configure API Key

Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/api-keys)

Then set it as an environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 3. Run the Demo

```bash
bun run dev
# Or simply: bun src/index.ts
```

**Bun Benefits:**
- ⚡ **Fast**: 3-4x faster than Node.js
- 📦 **No build step**: Runs TypeScript directly
- 🔥 **Hot reload**: Built-in watch mode
- 🎯 **All-in-one**: Runtime + package manager + test runner

## What You Should See

The demo runs three scenarios:

1. **Single image** → Auto-approved immediately
2. **5 images** → Pauses for approval → Approved
3. **10 images** → Pauses for approval → Rejected

## Troubleshooting

### "GOOGLE_API_KEY not found"

Make sure you've set the environment variable or created a `.env` file.

### "Cannot find module '@google/adk'"

Run `bun install` to install dependencies.

### MCP Connection Errors

The demo uses `npx` to run MCP servers. Bun has npx compatibility built-in. If you encounter issues, ensure you have the latest Bun version.

### Rate Limit Errors (429)

If you see rate limit errors:
- Wait a few seconds between runs
- Check your Gemini API quota at [Google AI Studio](https://aistudio.google.com/)

## Next Steps

### Modify the Tool

Edit `src/imageGenerationTool.ts` to change:
- Approval threshold (currently 1 image)
- Result messages
- Tool behavior

### Add Real UI

Replace the simulated approval in `src/workflow.ts` with:
- Web UI prompts
- Slack notifications
- Email confirmations

### Connect Real Image Generation

Replace the demo MCP server with actual image generation:
- DALL-E MCP server
- Stable Diffusion MCP server
- Other image generation APIs

### Build Production Features

Add:
- Database for storing pending approvals
- Webhook callbacks for async approval
- Audit logging
- Timeout handling
- Authentication

## Understanding the Code

### Entry Point: `src/index.ts`

Simple demo script that runs three test cases.

### Agent: `src/agent.ts`

Configures the LlmAgent with:
- Model (Gemini)
- Instructions
- Tools (imageGenerationTool + MCP)

### Tool: `src/imageGenerationTool.ts`

Implements the three-scenario pattern:
1. Auto-approve small requests
2. Pause for approval on bulk requests
3. Resume with approval decision

### Workflow: `src/workflow.ts`

Orchestrates the pause/resume cycle:
1. Run agent
2. Detect pause event
3. Get approval decision
4. Resume agent with same invocationId

## Resources

- [ADK TypeScript Docs](https://google.github.io/adk-docs/)
- [Original Python Notebook](https://www.kaggle.com/code/kaggle5daysofai/day-2b-agent-tools-best-practices)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Day 2 Video Tutorial](https://www.youtube.com/watch?v=44C8u0CDtSo)
