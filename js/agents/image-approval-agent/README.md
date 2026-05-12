# Image Generation Agent with Cost Approval

This project demonstrates how to build an AI agent using the Google ADK for TypeScript that handles image generation with approval workflows for bulk operations.

## 🎯 What This Demonstrates

This implementation showcases the **Long-Running Operation (LRO)** pattern from the ADK Day-2 course, adapted for TypeScript:

- ✅ **Auto-approval for small requests**: Single image requests complete immediately
- ⏸️ **Pause/Resume workflow**: Bulk requests (>1 images) pause to request human approval
- 🔄 **State management**: Agent maintains context across the pause/resume cycle
- 🔌 **MCP Integration**: Demonstrates connecting to external MCP servers

## 📁 Project Structure

```
image-approval-agent/
├── src/
│   ├── imageGenerationTool.ts   # Tool with approval logic
│   ├── agent.ts                 # Agent configuration with MCP
│   ├── workflow.ts              # Pause/resume workflow orchestration
│   └── index.ts                 # Demo entry point
├── package.json
├── tsconfig.json
└── README.md
```

## 🏗️ Architecture

### Three-Scenario Pattern

The `imageGenerationTool` implements the three-scenario pattern:

**Scenario 1: Small Request (≤1 image)**
- Returns immediately with auto-approved status
- No approval workflow triggered

**Scenario 2: First Call (Bulk Request)**
- Detects `toolContext.toolConfirmation` is undefined
- Calls `toolContext.requestConfirmation()` to pause
- Returns `{status: 'pending', ...}`
- ADK creates `adk_request_confirmation` event

**Scenario 3: Resumed Call**
- Detects `toolContext.toolConfirmation` is present
- Checks `toolContext.toolConfirmation.confirmed`
- Returns approved or rejected status

### Workflow Orchestration

The `ImageGenerationWorkflow` class handles:

1. **Initial execution**: Runs agent with user query
2. **Pause detection**: Scans events for `adk_request_confirmation`
3. **Approval simulation**: Gets human decision (in production, this would be a UI)
4. **Resume execution**: Calls agent again with same `invocationId`

## 🚀 Getting Started

### Prerequisites

- [Bun](https://bun.sh) 1.0+ (fast JavaScript runtime)
- Google API Key (Gemini API access)

### Installation

```bash
cd image-approval-agent
bun install
```

**Why Bun?** Bun is a fast all-in-one JavaScript runtime that's significantly faster than Node.js and has built-in TypeScript support.

### Environment Setup

Set your Google API key:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```
GOOGLE_API_KEY=your-api-key-here
```

### Running the Demo

```bash
# Run with Bun (TypeScript executed directly, no build needed!)
bun run dev

# Or use the npm-style script
bun start

# Or run directly
bun src/index.ts
```

**Note:** Bun has native TypeScript support, so you can run `.ts` files directly without transpiling!

## 📊 Example Output

```
🚀 Image Generation Agent with Cost Approval Demo

📸 Demo 1: Single Image Request (Auto-Approved)
============================================================
User > Generate 1 image of a sunset over mountains

Agent > Image generation auto-approved: 1 image for "a sunset over mountains"
============================================================

📸 Demo 2: Bulk Request with Approval (APPROVE)
============================================================
User > Generate 5 images of futuristic cities

⏸️  Pausing for approval...
⚠️ Bulk image generation request: 5 images for "futuristic cities". This may incur additional costs. Do you want to approve?
🤔 Human Decision: APPROVE ✅

Agent > Bulk image generation approved: 5 images for "futuristic cities"
============================================================

📸 Demo 3: Bulk Request with Rejection (REJECT)
============================================================
User > Generate 10 images of abstract art

⏸️  Pausing for approval...
⚠️ Bulk image generation request: 10 images for "abstract art". This may incur additional costs. Do you want to approve?
🤔 Human Decision: REJECT ❌

Agent > Bulk image generation rejected: 10 images for "abstract art"
============================================================
```

## 🔑 Key Concepts

### ToolContext

The `ToolContext` parameter is automatically provided by ADK and gives your tool:
- `toolContext.requestConfirmation()` - Pause execution and request approval
- `toolContext.toolConfirmation` - Check approval status on resume

### Invocation ID

Critical for resuming the correct execution:
- Generated automatically when you call `runner.runAsync()`
- Saved when agent pauses
- Passed back when resuming to continue the same execution

### Event Detection

The workflow looks for the special `adk_request_confirmation` function call:
```typescript
part.functionCall?.name === REQUEST_CONFIRMATION_FUNCTION_CALL_NAME
```

This signals the agent has paused and needs approval.

## 🔌 MCP Integration

This project uses the MCP (Model Context Protocol) to connect to external tools:

```typescript
new McpToolset({
  connectionParams: new StdioConnectionParams({
    serverParams: new StdioServerParameters({
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-everything'],
      toolFilter: ['getTinyImage'],
    }),
    timeout: 30000,
  }),
});
```

### Available MCP Servers

- **@modelcontextprotocol/server-everything** - Demo server with test tools
- For production, explore:
  - Image generation MCP servers
  - Kaggle MCP server (`mcp-remote https://www.kaggle.com/mcp`)
  - GitHub MCP server
  - [More at modelcontextprotocol.io](https://modelcontextprotocol.io/examples)

## 🎓 Learning Resources

This project is based on the Kaggle 5-Day Agents Course:
- [Day 2: Agent Tools and Best Practices](https://www.kaggle.com/code/kaggle5daysofai/day-2b-agent-tools-best-practices)
- [ADK Documentation](https://google.github.io/adk-docs/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

## 🛠️ Production Considerations

For production use, consider:

1. **Real UI Integration**: Replace simulated approval with actual UI
2. **Database Persistence**: Store pending approvals in a database
3. **Timeout Handling**: Add expiration for approval requests
4. **Audit Logging**: Log all approval decisions
5. **Error Handling**: Handle network failures, timeouts, etc.
6. **Authentication**: Secure approval endpoints
7. **Notification System**: Alert humans when approval is needed

## 📝 License

Apache 2.0 - See LICENSE file
