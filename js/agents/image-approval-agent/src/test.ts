/**
 * Minimal test to debug the issue
 */
import {LlmAgent, Gemini, InMemoryRunner, FunctionTool} from '@google/adk';
import {z} from 'zod';

// Simple test function without approval logic
const testTool = new FunctionTool({
  name: 'test_function',
  description: 'A simple test function',
  parameters: z.object({
    message: z.string(),
  }),
  execute: async (args) => {
    console.log('Tool called with:', args);
    return {result: `Received: ${args.message}`};
  },
});

// Create a simple agent
const testAgent = new LlmAgent({
  name: 'test_agent',
  model: new Gemini({model: 'gemini-2.5-flash'}),
  instruction: 'You are a test assistant. Use the test_function tool.',
  tools: [testTool],
});

// Run test
async function test() {
  console.log('🧪 Starting minimal test...\n');

  const appName = 'test_app';
  const userId = 'test_user';
  const runner = new InMemoryRunner({agent: testAgent, appName});

  const sessionId = `test_${Date.now()}`;

  await runner.sessionService.createSession({
    appName,
    userId,
    sessionId,
  });

  try {
    console.log('Sending message...');
    const events = [];
    for await (const event of runner.runAsync({
      userId,
      sessionId,
      newMessage: {
        role: 'user',
        parts: [{text: 'Say hello using the test function'}],
      },
    })) {
      events.push(event);
      console.log(`Event from ${event.author}:`, event.content?.parts?.[0]);
    }
    console.log('\n✅ Test completed successfully!');
  } catch (error) {
    console.error('❌ Test failed:', error);
    throw error;
  }
}

test().catch(console.error);
