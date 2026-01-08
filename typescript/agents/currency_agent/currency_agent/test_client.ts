/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Test client for the currency agent.
 * This demonstrates how to use the currency agent programmatically.
 * 
 * Note: This is a simple test that verifies the agent can be instantiated.
 * For full testing, use: npx adk run currency_agent/agent.ts
 */

import { rootAgent } from './agent';

/**
 * Main function to verify the agent is properly configured.
 */
async function main(): Promise<void> {
  console.log('--- 🔄 Initializing Currency Agent Test Client... ---');
  console.log('--- ✅ Verifying agent configuration... ---\n');

  try {
    // Verify agent is properly configured
    console.log('Agent Name:', rootAgent.name);
    console.log('Agent Model:', rootAgent.model);
    console.log('Agent Tools Count:', rootAgent.tools?.length || 0);
    
    if (rootAgent.tools && rootAgent.tools.length > 0) {
      console.log('Tools:');
      rootAgent.tools.forEach((tool: any) => {
        console.log(`  - ${tool.name || 'Unknown tool'}`);
      });
    }
    
    console.log('\n--- ✅ Agent is properly configured! ---');
    console.log('\nTo test the agent interactively, run:');
    console.log('  npx adk run currency_agent/agent.ts');
    console.log('\nOr use the agent programmatically in your own code.');
  } catch (error) {
    console.error('--- ❌ An error occurred: ---');
    console.error(error);
    console.error('\nEnsure:');
    console.error('1. Environment variables are set (GOOGLE_API_KEY or Vertex AI config)');
    console.error('2. Dependencies are installed (npm install)');
    process.exit(1);
  }
}

// Run the tests if this file is executed directly
if (require.main === module) {
  main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { main as testAgent };
