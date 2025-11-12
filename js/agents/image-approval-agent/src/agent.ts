/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {LlmAgent, Gemini, MCPToolset} from '@google/adk';
import type {StdioConnectionParams} from '@google/adk';
import {imageGenerationTool} from './imageGenerationTool.js';

/**
 * Creates the MCP toolset for the Everything MCP Server
 * This server provides a getTinyImage tool for testing
 *
 * In production, you would use an actual image generation MCP server
 */
function createMcpToolset(): MCPToolset {
  const connectionParams: StdioConnectionParams = {
    type: 'StdioConnectionParams',
    serverParams: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-everything'],
    },
    timeout: 30000, // 30 seconds timeout
  };

  return new MCPToolset(connectionParams, ['getTinyImage']);
}

/**
 * Creates the image generation agent with approval workflow
 *
 * The agent uses:
 * 1. Custom imageGenerationTool - Handles approval logic for bulk requests
 * 2. MCP Toolset - Provides access to external image generation services
 */
export function createImageAgent(): LlmAgent {
  const mcpToolset = createMcpToolset();

  return new LlmAgent({
    name: 'image_generation_agent',
    model: new Gemini({model: 'gemini-2.5-flash'}),
    instruction: `You are an image generation assistant.

When users request to generate images:
1. Use the generate_images tool to create images based on their text prompt
2. If the request status is 'pending', inform the user that approval is required for bulk generation
3. After receiving the final result, provide a clear summary including:
   - Generation status (approved/rejected)
   - Request ID (if available)
   - Number of images and prompt
4. For demonstration purposes, you can also use the getTinyImage tool from the MCP server
5. Keep responses concise but informative

IMPORTANT:
- Single image requests are auto-approved
- Bulk requests (>1 images) require approval before generation
- Always explain the status clearly to the user`,
    tools: [imageGenerationTool, mcpToolset],
  });
}
