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

import { z } from 'zod';
import { FunctionTool } from '@google/adk';
import { config } from '../config';

/**
 * MCP Tool for getting exchange rates.
 * This tool calls the MCP server to get currency exchange rates.
 */

const GetExchangeRateInput = z.object({
  currency_from: z.string().describe('The currency to convert from (e.g., "USD").'),
  currency_to: z.string().describe('The currency to convert to (e.g., "EUR").'),
  currency_date: z.string().optional().describe('The date for the exchange rate or "latest". Defaults to "latest".'),
});

interface ExchangeRateResponse {
  rates?: Record<string, number>;
  error?: string;
  [key: string]: any;
}

/**
 * Calls the MCP server to get exchange rate information.
 */
async function getExchangeRate({
  currency_from,
  currency_to,
  currency_date = 'latest',
}: {
  currency_from: string;
  currency_to: string;
  currency_date?: string;
}): Promise<ExchangeRateResponse> {
  console.log(
    `--- 🛠️ Tool: get_exchange_rate called for converting ${currency_from} to ${currency_to} ---`
  );

  try {
    // Call the MCP server
    const mcpUrl = config.MCP_SERVER_URL;
    const response = await fetch(`${mcpUrl}/tools/call`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: 'get_exchange_rate',
        arguments: {
          currency_from,
          currency_to,
          currency_date,
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Handle MCP response format
    if (data.content && Array.isArray(data.content)) {
      // MCP response format: { content: [{ type: "text", text: "..." }] }
      const textContent = data.content.find((c: any) => c.type === 'text');
      if (textContent) {
        const parsed = JSON.parse(textContent.text);
        if (!parsed.rates) {
          console.error(`❌ rates not found in response: ${parsed}`);
          return { error: 'Invalid API response format.' };
        }
        console.log(`✅ API response: ${JSON.stringify(parsed)}`);
        return parsed;
      }
    } else if (data.rates) {
      // Direct response format
      console.log(`✅ API response: ${JSON.stringify(data)}`);
      return data;
    } else {
      console.error(`❌ rates not found in response: ${data}`);
      return { error: 'Invalid API response format.' };
    }

    return { error: 'Invalid response format from MCP server.' };
  } catch (error) {
    console.error(`❌ API request failed: ${error}`);
    return { error: `API request failed: ${error instanceof Error ? error.message : String(error)}` };
  }
}

export const getExchangeRateTool = new FunctionTool({
  name: 'get_exchange_rate',
  description: 'Use this to get current exchange rate.',
  parameters: GetExchangeRateInput,
  execute: getExchangeRate,
});
