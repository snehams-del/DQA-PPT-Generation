/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {FunctionTool, ToolContext} from '@google/adk';
import {z} from 'zod';

/**
 * Threshold for determining if approval is needed.
 * Single image (1) auto-approves, bulk (>1) requires approval.
 */
const BULK_IMAGE_THRESHOLD = 1;

/**
 * Result type for image generation requests
 */
interface ImageGenerationResult {
  status: 'approved' | 'pending' | 'rejected';
  requestId?: string;
  numImages: number;
  prompt: string;
  message: string;
}

/**
 * Generates images based on a text prompt.
 *
 * This function implements the long-running operation pattern:
 * - Single image requests (1 image): Auto-approved, completes immediately
 * - Bulk requests (>1 images): Pauses to request human approval
 *
 * The function handles three scenarios:
 * 1. Small request (≤1 image): Returns immediately with auto-approved status
 * 2. First call for bulk request: Requests confirmation and returns pending status
 * 3. Resumed call after approval: Checks confirmation and returns final status
 *
 * @param numImages - Number of images to generate
 * @param prompt - Text description of the image to generate
 * @param toolContext - ADK tool context (automatically provided)
 * @returns Result object with status and details
 */
async function generateImages(
  args: {numImages: number; prompt: string},
  toolContext?: ToolContext
): Promise<ImageGenerationResult> {
  const {numImages, prompt} = args;

  if (!toolContext) {
    throw new Error('ToolContext is required for this function');
  }
  // -----------------------------------------------------------------------------------------------
  // SCENARIO 1: Single image requests (≤1) auto-approve
  // -----------------------------------------------------------------------------------------------
  if (numImages <= BULK_IMAGE_THRESHOLD) {
    return {
      status: 'approved',
      requestId: `IMG-${numImages}-AUTO-${Date.now()}`,
      numImages,
      prompt,
      message: `Image generation auto-approved: ${numImages} image for "${prompt}"`,
    };
  }

  // -----------------------------------------------------------------------------------------------
  // SCENARIO 2: This is the first time this tool is called. Bulk requests need approval - PAUSE here.
  // -----------------------------------------------------------------------------------------------
  if (!toolContext.toolConfirmation) {
    toolContext.requestConfirmation({
      hint: `⚠️ Bulk image generation request: ${numImages} images for "${prompt}". This may incur additional costs. Do you want to approve?`,
      payload: {numImages, prompt},
    });

    return {
      status: 'pending',
      numImages,
      prompt,
      message: `Bulk image generation (${numImages} images) requires approval. Awaiting confirmation...`,
    };
  }

  // -----------------------------------------------------------------------------------------------
  // SCENARIO 3: The tool is called AGAIN and is now resuming. Handle approval response - RESUME here.
  // -----------------------------------------------------------------------------------------------
  if (toolContext.toolConfirmation.confirmed) {
    return {
      status: 'approved',
      requestId: `IMG-${numImages}-HUMAN-${Date.now()}`,
      numImages,
      prompt,
      message: `Bulk image generation approved: ${numImages} images for "${prompt}"`,
    };
  } else {
    return {
      status: 'rejected',
      numImages,
      prompt,
      message: `Bulk image generation rejected: ${numImages} images for "${prompt}"`,
    };
  }
}

/**
 * Function tool that wraps the image generation function with schema validation
 */
export const imageGenerationTool = new FunctionTool({
  name: 'generate_images',
  description:
    'Generates images based on a text prompt. Single image requests are auto-approved. Bulk requests (>1 images) require approval.',
  parameters: z.object({
    numImages: z
      .number()
      .int()
      .positive()
      .describe('Number of images to generate'),
    prompt: z.string().describe('Text description of the image to generate'),
  }),
  execute: generateImages,
});
