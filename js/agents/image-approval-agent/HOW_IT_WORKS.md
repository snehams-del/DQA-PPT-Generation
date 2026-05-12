# How It Works: Step-by-Step Technical Walkthrough

This document provides a detailed, step-by-step explanation of how the Image Generation Agent with Cost Approval works.

## 📚 Table of Contents

1. [High-Level Overview](#high-level-overview)
2. [Component Breakdown](#component-breakdown)
3. [Execution Flow: Single Image (Auto-Approve)](#execution-flow-single-image-auto-approve)
4. [Execution Flow: Bulk Request (Pause/Resume)](#execution-flow-bulk-request-pauseresume)
5. [Key Technical Concepts](#key-technical-concepts)
6. [Code Deep Dive](#code-deep-dive)

---

## High-Level Overview

This project implements the **Long-Running Operation (LRO)** pattern for AI agents. It demonstrates how to:

1. Create tools that can **pause** execution
2. Wait for **external input** (human approval)
3. **Resume** execution with the decision
4. Integrate with **external services** via MCP

### The Core Pattern

```
User Request → Agent Calls Tool → Tool Logic Decision:
                                   ├─ Small request? → Complete immediately
                                   └─ Large request? → Pause → Wait for approval → Resume → Complete
```

---

## Component Breakdown

### 1. Tool (`imageGenerationTool.ts`)

**Purpose**: Wraps the image generation function with approval logic

**Key Parts**:
- `generateImages()` function - Core logic with three scenarios
- `FunctionTool` wrapper - Provides schema validation via Zod
- `ToolContext` parameter - ADK-provided context for pause/resume

### 2. Agent (`agent.ts`)

**Purpose**: Configures the AI agent with model, instructions, and tools

**Key Parts**:
- `LlmAgent` - Main agent class from ADK
- `Gemini` model - The LLM that powers the agent
- Tools array - Contains both custom tool and MCP toolset
- Instructions - Guides agent behavior

### 3. Workflow (`workflow.ts`)

**Purpose**: Orchestrates the pause/resume cycle

**Key Parts**:
- `ImageGenerationWorkflow` class - Manages the entire flow
- `checkForApproval()` - Detects pause events
- `createApprovalResponse()` - Formats approval decision
- `run()` - Main execution method

### 4. Entry Point (`index.ts`)

**Purpose**: Demo script showing three scenarios

---

## Execution Flow: Single Image (Auto-Approve)

Let's trace what happens when user says: **"Generate 1 image of a sunset"**

### Timeline

```
[TIME 1] User sends message
         ↓
[TIME 2] Workflow.run() is called
         ↓
[TIME 3] Session created with unique ID
         session_id = "img_1234567890_abc123"
         ↓
[TIME 4] Message formatted as Content object
         {
           role: 'user',
           parts: [{text: 'Generate 1 image of a sunset'}]
         }
         ↓
[TIME 5] runner.runAsync() called
         - ADK assigns invocation_id = "inv_xyz789"
         - Agent receives the message
         ↓
[TIME 6] Agent (Gemini) analyzes the request
         Decision: "User wants 1 image, I should use generate_images tool"
         ↓
[TIME 7] Agent creates function call
         {
           name: 'generate_images',
           args: {
             numImages: 1,
             prompt: 'a sunset'
           }
         }
         ↓
[TIME 8] ADK executes generateImages(1, 'a sunset', toolContext)
         ↓
[TIME 9] Tool checks: numImages (1) <= BULK_IMAGE_THRESHOLD (1)
         ✅ SCENARIO 1: Auto-approve path
         ↓
[TIME 10] Tool returns immediately
          {
            status: 'approved',
            requestId: 'IMG-1-AUTO-1234567890',
            numImages: 1,
            prompt: 'a sunset',
            message: 'Image generation auto-approved: 1 image for "a sunset"'
          }
          ↓
[TIME 11] ADK creates function_response event
          Agent receives the tool result
          ↓
[TIME 12] Agent (Gemini) processes result
          Generates response: "Image generation auto-approved: 1 image..."
          ↓
[TIME 13] Event with agent's text response returned
          ↓
[TIME 14] Workflow receives all events
          ↓
[TIME 15] checkForApproval(events) called
          Result: undefined (no adk_request_confirmation found)
          ↓
[TIME 16] Workflow takes PATH B: No approval needed
          printAgentResponse(events) displays the text
          ↓
[TIME 17] ✅ COMPLETE
```

### Key Observation

- Tool completed immediately at TIME 10
- No pause occurred
- Only ONE call to `runner.runAsync()`
- Execution is linear from start to finish

---

## Execution Flow: Bulk Request (Pause/Resume)

Let's trace what happens when user says: **"Generate 5 images of futuristic cities"**

This is where the magic happens!

### Phase 1: Initial Request (Leading to Pause)

```
[TIME 1] User sends message
         ↓
[TIME 2] Workflow.run() called with autoApprove=true
         ↓
[TIME 3] Session created: session_id = "img_1234567890_def456"
         ↓
[TIME 4] First runner.runAsync() called
         ADK assigns: invocation_id = "inv_abc123"
         ↓
[TIME 5] Agent analyzes request
         Decision: "User wants 5 images, use generate_images tool"
         ↓
[TIME 6] Function call created
         {
           name: 'generate_images',
           args: {
             numImages: 5,
             prompt: 'futuristic cities'
           }
         }
         ↓
[TIME 7] ADK executes generateImages(5, 'futuristic cities', toolContext)
         ↓
[TIME 8] Tool checks: numImages (5) > BULK_IMAGE_THRESHOLD (1)
         ✅ Bulk request detected!
         ↓
[TIME 9] Tool checks: toolContext.toolConfirmation
         Result: undefined (first call)
         ✅ SCENARIO 2: First call - need approval
         ↓
[TIME 10] Tool calls toolContext.requestConfirmation()
          Parameters passed:
          {
            hint: "⚠️ Bulk image generation request: 5 images...",
            payload: {
              numImages: 5,
              prompt: 'futuristic cities'
            }
          }
          ↓
[TIME 11] ⚠️ CRITICAL: ADK internally marks this as "paused"
          - Saves current execution state
          - Saves invocation_id = "inv_abc123"
          - Saves tool parameters
          ↓
[TIME 12] Tool returns immediately (doesn't wait!)
          {
            status: 'pending',
            numImages: 5,
            prompt: 'futuristic cities',
            message: 'Bulk image generation (5 images) requires approval...'
          }
          ↓
[TIME 13] ADK creates TWO events:

          Event 1: function_call event with tool response
          Event 2: SPECIAL event with function_call:
          {
            name: 'adk_request_confirmation',
            id: 'conf_xyz789',  // This ID is critical!
            args: {
              hint: "⚠️ Bulk image generation request...",
              payload: {...}
            }
          }
          ↓
[TIME 14] Agent receives "pending" status
          Generates text: "Bulk image generation requires approval..."
          ↓
[TIME 15] First runAsync() completes
          Returns array of events (including the special one)
          ↓
[TIME 16] ⏸️ EXECUTION PAUSED - Agent is waiting
```

### Phase 2: Workflow Detects Pause

```
[TIME 17] Workflow receives events array
          ↓
[TIME 18] checkForApproval(events) called
          Loops through all events looking for:
          part.functionCall?.name === 'adk_request_confirmation'
          ↓
[TIME 19] ✅ FOUND IT!
          Extracts:
          {
            approvalId: 'conf_xyz789',
            invocationId: 'inv_abc123',  // Same as original!
            hint: '⚠️ Bulk image generation request...'
          }
          ↓
[TIME 20] Workflow enters approval handling block
          Prints: "⏸️ Pausing for approval..."
          Prints the hint
          ↓
[TIME 21] Simulated human decision made
          autoApprove = true → Decision is APPROVE ✅

          (In production, this would be:
           - Show UI modal
           - Wait for user click
           - Could be minutes/hours later!)
```

### Phase 3: Resume Execution

```
[TIME 22] createApprovalResponse() called
          Creates a function_response Content object:
          {
            role: 'user',
            parts: [{
              functionResponse: {
                id: 'conf_xyz789',  // Same approval ID!
                name: 'adk_request_confirmation',
                response: {
                  confirmed: true  // The human decision
                }
              }
            }]
          }
          ↓
[TIME 23] ⚡ CRITICAL: Second runner.runAsync() called
          Parameters:
          - newMessage: approval response from TIME 22
          - invocationId: 'inv_abc123'  ← SAME as TIME 4!

          This tells ADK: "Don't start new execution, RESUME the paused one!"
          ↓
[TIME 24] ADK sees invocation_id matches paused execution
          - Loads saved state from TIME 11
          - Restores: tool call, parameters, conversation history
          - Continues from where it paused
          ↓
[TIME 25] ADK calls generateImages(5, 'futuristic cities', toolContext)
          But now toolContext is different!
          ↓
[TIME 26] Tool checks: toolContext.toolConfirmation
          Result: NOT undefined!
          {
            confirmed: true,
            hint: '...',
            payload: {...}
          }
          ✅ SCENARIO 3: Resumed call - check decision
          ↓
[TIME 27] Tool checks: toolContext.toolConfirmation.confirmed
          Result: true
          ↓
[TIME 28] Tool returns approved result
          {
            status: 'approved',
            requestId: 'IMG-5-HUMAN-1234567890',
            numImages: 5,
            prompt: 'futuristic cities',
            message: 'Bulk image generation approved: 5 images...'
          }
          ↓
[TIME 29] Agent receives tool result
          Generates final response: "Bulk image generation approved..."
          ↓
[TIME 30] Second runAsync() completes
          Workflow prints agent's response
          ↓
[TIME 31] ✅ COMPLETE
```

### Key Observations

1. **Two separate calls to `runner.runAsync()`**:
   - First call → Pauses at TIME 16
   - Second call → Resumes at TIME 23

2. **Same `invocationId` is crucial**:
   - Assigned at TIME 4: "inv_abc123"
   - Saved in approval info at TIME 19
   - Passed back at TIME 23
   - ADK uses this to know which execution to resume

3. **Tool called twice**:
   - First call (TIME 7): `toolContext.toolConfirmation` is undefined
   - Second call (TIME 25): `toolContext.toolConfirmation` has the decision

4. **Time can pass**: Between TIME 21 and TIME 23, arbitrary time can elapse (minutes, hours, days)

---

## Key Technical Concepts

### 1. InvocationId

**What it is**: A unique identifier for each agent execution

**Why it matters**:
- Without it, ADK would start a NEW execution instead of resuming
- Like a "save game" ID - tells ADK which paused execution to continue

**Flow**:
```typescript
// First call - ADK generates this
await runner.runAsync({...})  // invocation_id = "inv_123" assigned internally

// Second call - We provide the same one
await runner.runAsync({
  invocationId: "inv_123"  // Resume execution "inv_123"
})
```

### 2. ToolContext

**What it is**: An object ADK automatically provides to your tool function

**Properties**:
- `toolContext.requestConfirmation(...)` - Method to pause
- `toolContext.toolConfirmation` - Property to check approval status

**Lifecycle**:

| Call | toolContext.toolConfirmation | What to do |
|------|------------------------------|------------|
| First | `undefined` | Call `requestConfirmation()` and return pending |
| Second | `{confirmed: true/false, ...}` | Check decision and return final result |

### 3. The Special Event: `adk_request_confirmation`

**What it is**: A special function_call event that ADK creates automatically when your tool calls `requestConfirmation()`

**Structure**:
```typescript
{
  functionCall: {
    name: 'adk_request_confirmation',  // Special name
    id: 'conf_xyz789',                 // Unique approval ID
    args: {
      hint: 'User-facing message',
      payload: {...}                    // Data you passed
    }
  }
}
```

**Why it's special**:
- It's the signal that execution has paused
- Your workflow MUST detect this event
- The `id` field becomes the `approvalId` you send back

### 4. Session vs Invocation

**Session**:
- Represents an entire conversation
- Can contain multiple invocations
- Persists conversation history

**Invocation**:
- One call to `runAsync()`
- Can be paused and resumed
- Part of a session

**Example**:
```
Session "img_123":
  ├─ Invocation "inv_001": "Generate 1 image" (completed)
  ├─ Invocation "inv_002": "Generate 5 images" (paused)
  └─ Invocation "inv_002": (resumed with approval)
```

### 5. Content and Parts

**Content**: A message in the conversation

```typescript
type Content = {
  role: 'user' | 'model',
  parts: Part[]
}
```

**Part**: A piece of content (text, function call, function response)

```typescript
type Part =
  | {text: string}
  | {functionCall: {...}}
  | {functionResponse: {...}}
```

**Flow**:
```
User message → Content with text Part
Agent tool call → Content with functionCall Part
Tool result → Content with functionResponse Part
Agent text → Content with text Part
```

---

## Code Deep Dive

### Tool: The Three Scenarios

```typescript
async function generateImages(
  numImages: number,
  prompt: string,
  toolContext: ToolContext
): Promise<ImageGenerationResult> {

  // SCENARIO 1: Auto-approve small requests
  if (numImages <= BULK_IMAGE_THRESHOLD) {
    // This is the ONLY scenario where we don't check toolContext.toolConfirmation
    // Just return immediately - no pause
    return {
      status: 'approved',
      requestId: `IMG-${numImages}-AUTO-${Date.now()}`,
      ...
    };
  }

  // SCENARIO 2: First call - request approval
  // toolContext.toolConfirmation is undefined the first time tool is called
  if (!toolContext.toolConfirmation) {
    // This triggers ADK to:
    // 1. Save current state
    // 2. Create adk_request_confirmation event
    // 3. Mark execution as paused
    toolContext.requestConfirmation(
      new ToolConfirmation({
        hint: '⚠️ Bulk image generation request...',
        payload: {numImages, prompt}
      })
    );

    // Return immediately - don't wait for approval!
    // The workflow will detect the pause and handle it
    return {
      status: 'pending',
      message: 'Awaiting approval...'
    };
  }

  // SCENARIO 3: Resumed call - check decision
  // toolContext.toolConfirmation is NOW populated with human decision
  // ADK loaded this from the saved state
  if (toolContext.toolConfirmation.confirmed) {
    return {
      status: 'approved',
      requestId: `IMG-${numImages}-HUMAN-${Date.now()}`,
      ...
    };
  } else {
    return {
      status: 'rejected',
      ...
    };
  }
}
```

### Workflow: Detecting the Pause

```typescript
private checkForApproval(events: Event[]): ApprovalInfo | undefined {
  // Loop through ALL events from the agent execution
  for (const event of events) {
    if (!event.content?.parts) continue;

    // Each event can have multiple parts
    for (const part of event.content.parts) {
      // Look for the special function_call with specific name
      if (part.functionCall?.name === REQUEST_CONFIRMATION_FUNCTION_CALL_NAME) {

        // Extract the critical information:
        return {
          approvalId: part.functionCall.id ?? '',      // For the response
          invocationId: event.invocationId ?? '',       // To resume
          hint: part.functionCall.args?.hint as string  // User message
        };
      }
    }
  }

  // If we reach here, no approval request found
  return undefined;
}
```

### Workflow: Resuming Execution

```typescript
async run(query: string, autoApprove: boolean = true): Promise<void> {
  // ... session setup ...

  const events: Event[] = [];

  // STEP 1: Initial execution
  for await (const event of this.runner.runAsync({
    userId: this.userId,
    sessionId,
    newMessage: queryContent,
    // NOTE: No invocationId here - ADK will generate one
  })) {
    events.push(event);
  }

  // STEP 2: Check if we paused
  const approvalInfo = this.checkForApproval(events);

  if (approvalInfo) {
    // STEP 3A: We paused - simulate human decision
    console.log('⏸️  Pausing for approval...');

    // In production, you would:
    // - Store approvalInfo in database
    // - Show UI to user
    // - Wait for webhook callback
    // - Load approvalInfo from database
    // - Continue below

    const approved = autoApprove; // Simulated decision

    // STEP 4: Resume execution
    for await (const event of this.runner.runAsync({
      userId: this.userId,
      sessionId,
      newMessage: this.createApprovalResponse(approvalInfo, approved),
      invocationId: approvalInfo.invocationId,  // ← THE KEY!
      // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      // This tells ADK: "Resume inv_abc123, don't start new execution"
    })) {
      // Display resumed execution results
      if (event.content?.parts) {
        for (const part of event.content.parts) {
          if (part.text) {
            console.log(`Agent > ${part.text}`);
          }
        }
      }
    }
  } else {
    // STEP 3B: No pause - just display results
    this.printAgentResponse(events);
  }
}
```

### Creating the Approval Response

```typescript
private createApprovalResponse(
  approvalInfo: ApprovalInfo,
  approved: boolean
): Content {
  // Create a FunctionResponse that matches the adk_request_confirmation call
  const functionResponse: FunctionResponse = {
    id: approvalInfo.approvalId,  // MUST match the function_call id
    name: REQUEST_CONFIRMATION_FUNCTION_CALL_NAME,
    response: {
      confirmed: approved  // The human decision: true or false
    }
  };

  // Wrap it in a Content object as a user message
  return {
    role: 'user',  // Pretend the user sent this response
    parts: [{functionResponse}] as Part[]
  };
}
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER REQUEST                         │
│              "Generate 5 images of cities"                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW.run()                            │
│  1. Create session                                           │
│  2. Call runner.runAsync() with user message                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   AGENT (Gemini)                             │
│  Analyzes request → Decides to use generate_images tool      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             TOOL: generateImages() - FIRST CALL              │
│  1. Check: numImages (5) > threshold (1) ✓                   │
│  2. Check: toolContext.toolConfirmation → undefined          │
│  3. Call: toolContext.requestConfirmation()                  │
│  4. Return: {status: 'pending', ...}                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ADK FRAMEWORK                             │
│  1. Saves execution state (invocation_id = "inv_123")        │
│  2. Creates adk_request_confirmation event                   │
│  3. Returns events array to workflow                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            WORKFLOW.checkForApproval()                       │
│  1. Scans events for adk_request_confirmation                │
│  2. Finds it! Extracts approvalId and invocationId           │
│  3. Returns approval info                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  ⏸️  PAUSE POINT                              │
│                                                              │
│  In production: Store in DB, show UI, wait for user click   │
│  In demo: Simulate decision immediately                      │
│                                                              │
│  Time can pass: seconds, minutes, hours, days...            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               HUMAN DECISION: APPROVE ✅                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         WORKFLOW.createApprovalResponse()                    │
│  Creates FunctionResponse with confirmed: true               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│       WORKFLOW.run() - SECOND runAsync() CALL                │
│  Call runner.runAsync() WITH:                                │
│  - newMessage: approval response                             │
│  - invocationId: "inv_123" (SAME AS BEFORE)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ADK FRAMEWORK                             │
│  1. Sees invocationId matches saved execution                │
│  2. Loads saved state from before pause                      │
│  3. Restores: tool call, parameters, conversation            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            TOOL: generateImages() - SECOND CALL              │
│  1. Check: numImages (5) > threshold (1) ✓                   │
│  2. Check: toolContext.toolConfirmation → EXISTS!            │
│     {confirmed: true, ...}                                   │
│  3. Check: confirmed === true ✓                              │
│  4. Return: {status: 'approved', requestId: '...', ...}      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   AGENT (Gemini)                             │
│  Receives tool result → Generates response text              │
│  "Bulk image generation approved: 5 images..."               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW.run()                            │
│  1. Receives events from second runAsync()                   │
│  2. Displays agent's response                                │
│  3. ✅ COMPLETE                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

The entire system works through:

1. **Tool Logic**: Three scenarios based on `toolContext.toolConfirmation`
2. **ADK Magic**: Automatically saves/restores state using `invocationId`
3. **Workflow Detection**: Scans events for `adk_request_confirmation`
4. **Resume Pattern**: Second `runAsync()` call with same `invocationId`

The key insight: **The tool is called twice** - once to pause, once to complete. ADK handles all the state management in between!
