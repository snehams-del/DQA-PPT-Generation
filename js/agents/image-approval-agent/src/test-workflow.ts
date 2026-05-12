import {ImageGenerationWorkflow} from './workflow.js';

async function main() {
  console.log('\n🔍 Testing Single Image Request (Auto-Approved)');
  const workflow = new ImageGenerationWorkflow();
  await workflow.run('Generate 1 image of a sunset over mountains');
  await workflow.cleanup();
}

main().catch(console.error);
