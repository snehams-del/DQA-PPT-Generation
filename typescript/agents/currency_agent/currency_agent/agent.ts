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
 * Agent module for the currency agent.
 */

import { LlmAgent } from '@google/adk';
import { config } from './config';
import { getExchangeRateTool } from './tools/mcp_tool';

const SYSTEM_INSTRUCTION = `You are a specialized assistant for currency conversions. 
Your sole purpose is to use the 'get_exchange_rate' tool to answer questions about currency exchange rates. 
If the user asks about anything other than currency conversion or exchange rates, 
politely state that you cannot help with that topic and can only assist with currency-related queries. 
Do not attempt to answer unrelated questions or use tools for other purposes.`;

console.log('--- 🔧 Loading MCP tools from MCP Server... ---');
console.log('--- 🤖 Creating ADK Currency Agent... ---');

export const rootAgent = new LlmAgent({
  model: config.agentSettings.model,
  name: config.agentSettings.name,
  description: 'An agent that can help with currency conversions',
  instruction: SYSTEM_INSTRUCTION,
  tools: [getExchangeRateTool],
});
