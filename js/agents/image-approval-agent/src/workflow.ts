/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  InMemoryRunner,
  Event,
  REQUEST_CONFIRMATION_FUNCTION_CALL_NAME,
} from '@google/adk';
import type {Content, Part, FunctionResponse} from '@google/genai';
import {createImageAgent} from './agent.js';

/**
 * Information about a pending approval request
 */
interface ApprovalInfo {
  approvalId: string;
  invocationId: string;
  hint?: string;
}

/**
 * Workflow orchestrator for the image generation agent
 * Handles the pause/resume pattern for approval workflows
 */
export class ImageGenerationWorkflow {
  private runner: InMemoryRunner;
  private readonly appName = 'image_generation_app';
  private readonly userId = 'demo_user';

  constructor() {
    const agent = createImageAgent();
    this.runner = new InMemoryRunner({agent, appName: this.appName});
  }

  /**
   * Checks if events contain an approval request
   * Looks for the special 'adk_request_confirmation' function call
   *
   * @param events - Array of events from agent execution
   * @returns Approval info if found, undefined otherwise
   */
  private checkForApproval(events: Event[]): ApprovalInfo | undefined {
    for (const event of events) {
      if (!event.content?.parts) continue;

      for (const part of event.content.parts) {
        if (
          part.functionCall?.name === REQUEST_CONFIRMATION_FUNCTION_CALL_NAME
        ) {
          const hint =
            part.functionCall.args && 'hint' in part.functionCall.args
              ? (part.functionCall.args.hint as string)
              : undefined;

          return {
            approvalId: part.functionCall.id ?? '',
            invocationId: event.invocationId ?? '',
            hint,
          };
        }
      }
    }
    return undefined;
  }

  /**
   * Prints the agent's text responses from events
   *
   * @param events - Array of events to process
   */
  private printAgentResponse(events: Event[]): void {
    for (const event of events) {
      if (!event.content?.parts) continue;

      for (const part of event.content.parts) {
        if (part.text) {
          console.log(`Agent > ${part.text}`);
        }
      }
    }
  }

  /**
   * Creates an approval response message
   *
   * @param approvalInfo - The approval request info
   * @param approved - Whether the request was approved
   * @returns Content object with the approval response
   */
  private createApprovalResponse(
    approvalInfo: ApprovalInfo,
    approved: boolean
  ): Content {
    const functionResponse: FunctionResponse = {
      id: approvalInfo.approvalId,
      name: REQUEST_CONFIRMATION_FUNCTION_CALL_NAME,
      response: {confirmed: approved},
    };

    return {
      role: 'user',
      parts: [{functionResponse}] as Part[],
    };
  }

  /**
   * Runs the image generation workflow with approval handling
   *
   * @param query - User's image generation request
   * @param autoApprove - Whether to auto-approve bulk requests (simulates human decision)
   */
  async run(query: string, autoApprove: boolean = true): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log(`User > ${query}\n`);

    // Generate unique session ID
    const sessionId = `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Create session
    await this.runner.sessionService.createSession({
      appName: this.appName,
      userId: this.userId,
      sessionId: sessionId,
    });

    const queryContent: Content = {
      role: 'user',
      parts: [{text: query}],
    };

    const events: Event[] = [];

    // -----------------------------------------------------------------------------------------------
    // STEP 1: Send initial request to the Agent
    // If numImages > 1, the Agent returns the special 'adk_request_confirmation' event
    // -----------------------------------------------------------------------------------------------
    for await (const event of this.runner.runAsync({
      userId: this.userId,
      sessionId,
      newMessage: queryContent,
    })) {
      events.push(event);
    }

    // -----------------------------------------------------------------------------------------------
    // STEP 2: Check if approval is needed
    // Look for the 'adk_request_confirmation' event in the returned events
    // -----------------------------------------------------------------------------------------------
    const approvalInfo = this.checkForApproval(events);

    // -----------------------------------------------------------------------------------------------
    // STEP 3: Handle approval workflow if needed
    // -----------------------------------------------------------------------------------------------
    if (approvalInfo) {
      console.log('⏸️  Pausing for approval...');
      if (approvalInfo.hint) {
        console.log(`${approvalInfo.hint}`);
      }
      console.log(
        `🤔 Human Decision: ${autoApprove ? 'APPROVE ✅' : 'REJECT ❌'}\n`
      );

      // Resume the agent by calling runAsync() again with the approval decision
      // Note: The runner automatically handles resumption based on the session's last function call
      for await (const event of this.runner.runAsync({
        userId: this.userId,
        sessionId,
        newMessage: this.createApprovalResponse(approvalInfo, autoApprove),
      })) {
        if (event.content?.parts) {
          for (const part of event.content.parts) {
            if (part.text) {
              console.log(`Agent > ${part.text}`);
            }
          }
        }
      }
    } else {
      // No approval needed - order completed immediately
      this.printAgentResponse(events);
    }

    console.log('='.repeat(60) + '\n');
  }

  /**
   * Cleanup resources
   */
  async cleanup(): Promise<void> {
    // Close MCP connections if needed
  }
}
