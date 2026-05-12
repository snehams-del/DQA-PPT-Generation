# Quick Reference Guide

## Cheat Sheet for Long-Running Operations

### The Three-Scenario Pattern

```typescript
async function myTool(param: number, toolContext: ToolContext) {
  // SCENARIO 1: No approval needed
  if (param <= THRESHOLD) {
    return {status: 'approved', ...};
  }

  // SCENARIO 2: First call - request approval
  if (!toolContext.toolConfirmation) {
    toolContext.requestConfirmation(
      new ToolConfirmation({
        hint: 'User-facing message',
        payload: {param}
      })
    );
    return {status: 'pending', ...};
  }

  // SCENARIO 3: Second call - check decision
  if (toolContext.toolConfirmation.confirmed) {
    return {status: 'approved', ...};
  } else {
    return {status: 'rejected', ...};
  }
}
```

### Workflow Pattern

```typescript
// Step 1: Initial execution
const events: Event[] = [];
for await (const event of runner.runAsync({
  userId,
  sessionId,
  newMessage: userQuery
})) {
  events.push(event);
}

// Step 2: Check for pause
const approval = checkForApproval(events);

// Step 3: Resume if paused
if (approval) {
  const decision = await getHumanDecision(); // Your logic here

  for await (const event of runner.runAsync({
    userId,
    sessionId,
    newMessage: createApprovalResponse(approval, decision),
    invocationId: approval.invocationId  // CRITICAL!
  })) {
    // Handle resumed execution
  }
}
```

### Detecting the Pause Event

```typescript
function checkForApproval(events: Event[]): ApprovalInfo | undefined {
  for (const event of events) {
    for (const part of event.content?.parts ?? []) {
      if (part.functionCall?.name === 'adk_request_confirmation') {
        return {
          approvalId: part.functionCall.id,
          invocationId: event.invocationId,
          hint: part.functionCall.args?.hint
        };
      }
    }
  }
  return undefined;
}
```

### Creating Approval Response

```typescript
function createApprovalResponse(
  approval: ApprovalInfo,
  approved: boolean
): Content {
  return {
    role: 'user',
    parts: [{
      functionResponse: {
        id: approval.approvalId,
        name: 'adk_request_confirmation',
        response: {confirmed: approved}
      }
    }]
  };
}
```

## Common Patterns

### Pattern 1: Simple Auto-Approve Threshold

```typescript
const THRESHOLD = 5;

if (value <= THRESHOLD) {
  // Auto-approve
} else if (!toolContext.toolConfirmation) {
  // Request approval
} else {
  // Handle decision
}
```

### Pattern 2: Multi-Criteria Approval

```typescript
const needsApproval = (
  quantity > QUANTITY_THRESHOLD ||
  cost > COST_THRESHOLD ||
  isHighRisk(item)
);

if (!needsApproval) {
  return {status: 'approved'};
}

if (!toolContext.toolConfirmation) {
  toolContext.requestConfirmation(...);
  return {status: 'pending'};
}

// Handle decision...
```

### Pattern 3: Time-Based Approval

```typescript
if (isBusinessHours() && amount < AUTO_APPROVE_LIMIT) {
  return {status: 'approved'};
}

// Otherwise require approval
```

## Key Objects Reference

### ToolContext

```typescript
interface ToolContext {
  // Request approval (call in SCENARIO 2)
  requestConfirmation(confirmation: ToolConfirmation): void;

  // Check approval status (read in SCENARIO 3)
  toolConfirmation?: ToolConfirmation;

  // Other ADK context
  invocationContext: InvocationContext;
  actions: EventActions;
}
```

### ToolConfirmation

```typescript
class ToolConfirmation {
  constructor(params: {
    hint: string;        // User-facing message
    payload?: unknown;   // Data to preserve
    confirmed?: boolean; // Only set on resume
  })
}
```

### Event Structure

```typescript
interface Event {
  id: string;
  invocationId?: string;  // Critical for resume!
  author: string;
  content?: Content;
  timestamp: number;
  // ... other fields
}

interface Content {
  role: 'user' | 'model';
  parts: Part[];
}

type Part =
  | {text: string}
  | {functionCall: FunctionCall}
  | {functionResponse: FunctionResponse};
```

## Debugging Tips

### 1. Check Event Types

```typescript
for (const event of events) {
  console.log(`Event from: ${event.author}`);
  for (const part of event.content?.parts ?? []) {
    if (part.text) console.log('  - Text:', part.text);
    if (part.functionCall) console.log('  - Call:', part.functionCall.name);
    if (part.functionResponse) console.log('  - Response:', part.functionResponse.name);
  }
}
```

### 2. Verify InvocationId

```typescript
console.log('Initial invocation:', events[0]?.invocationId);
console.log('Approval invocation:', approvalInfo?.invocationId);
// These MUST match for resume to work!
```

### 3. Check ToolContext State

```typescript
async function myTool(..., toolContext: ToolContext) {
  console.log('Tool called with confirmation:',
    toolContext.toolConfirmation ? 'YES' : 'NO');

  if (toolContext.toolConfirmation) {
    console.log('  Confirmed:', toolContext.toolConfirmation.confirmed);
    console.log('  Payload:', toolContext.toolConfirmation.payload);
  }
}
```

## Common Mistakes

### ❌ Mistake 1: Not passing invocationId on resume

```typescript
// WRONG - starts new execution
await runner.runAsync({
  sessionId,
  newMessage: approvalResponse
  // Missing invocationId!
});

// CORRECT - resumes existing execution
await runner.runAsync({
  sessionId,
  newMessage: approvalResponse,
  invocationId: approvalInfo.invocationId  // ✓
});
```

### ❌ Mistake 2: Wrong approval ID

```typescript
// WRONG - IDs don't match
const response = {
  id: 'some-random-id',  // ✗
  name: 'adk_request_confirmation',
  response: {confirmed: true}
};

// CORRECT - use the ID from the pause event
const response = {
  id: approvalInfo.approvalId,  // ✓
  name: 'adk_request_confirmation',
  response: {confirmed: true}
};
```

### ❌ Mistake 3: Not collecting all events

```typescript
// WRONG - might miss the approval event
const lastEvent = await runner.runAsync(...);

// CORRECT - collect all events
const events: Event[] = [];
for await (const event of runner.runAsync(...)) {
  events.push(event);
}
```

### ❌ Mistake 4: Forgetting to check toolConfirmation

```typescript
// WRONG - doesn't handle resume case
async function myTool(..., toolContext: ToolContext) {
  if (needsApproval) {
    toolContext.requestConfirmation(...);
    return {status: 'pending'};
  }
  // Missing: what if toolContext.toolConfirmation exists?
}

// CORRECT - handle all three scenarios
async function myTool(..., toolContext: ToolContext) {
  if (!needsApproval) return {status: 'approved'};
  if (!toolContext.toolConfirmation) {
    toolContext.requestConfirmation(...);
    return {status: 'pending'};
  }
  // Handle the confirmation decision
  if (toolContext.toolConfirmation.confirmed) {
    return {status: 'approved'};
  } else {
    return {status: 'rejected'};
  }
}
```

## Production Checklist

- [ ] Store pending approvals in database
- [ ] Implement timeout for approval requests
- [ ] Add retry logic for failed resumes
- [ ] Handle edge cases (session expired, etc.)
- [ ] Add audit logging for all approvals
- [ ] Implement approval notifications (email/Slack/etc.)
- [ ] Secure approval endpoints with authentication
- [ ] Add approval history UI
- [ ] Handle concurrent approval requests
- [ ] Add approval delegation workflow
- [ ] Implement approval escalation
- [ ] Add analytics for approval patterns

## Testing Checklist

- [ ] Test auto-approve path (Scenario 1)
- [ ] Test pause/resume path (Scenarios 2 & 3)
- [ ] Test approval accepted
- [ ] Test approval rejected
- [ ] Test multiple approvals in same session
- [ ] Test session expiration during pause
- [ ] Test invalid invocationId
- [ ] Test missing approval response
- [ ] Test concurrent requests
- [ ] Test agent with multiple tools requiring approval
