/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {ImageGenerationWorkflow} from './workflow.js';

/**
 * Main entry point - demonstrates the image generation agent with approval workflow
 */
async function main() {
  console.log('🚀 Image Generation Agent with Cost Approval Demo\n');
  console.log(
    'This demo shows how to build agents that pause for approval on bulk operations.\n'
  );

  const workflow = new ImageGenerationWorkflow();

  try {
    // Demo 1: Single image request - auto-approves
    console.log('📸 Demo 1: Single Image Request (Auto-Approved)');
    await workflow.run('Generate 1 image of a sunset over mountains');

    // Demo 2: Bulk request with approval
    console.log('\n📸 Demo 2: Bulk Request with Approval (APPROVE)');
    await workflow.run(
      'Generate 5 images of futuristic cities',
      true // Auto-approve = true
    );

    // Demo 3: Bulk request rejected
    console.log('\n📸 Demo 3: Bulk Request with Rejection (REJECT)');
    await workflow.run(
      'Generate 10 images of abstract art',
      false // Auto-approve = false
    );

    console.log('\n✅ All demos completed successfully!');
  } catch (error) {
    console.error('❌ Error running workflow:', error);
  } finally {
    await workflow.cleanup();
  }
}

// Run the demo
main().catch(console.error);
